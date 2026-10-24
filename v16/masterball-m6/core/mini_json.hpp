// Minimal flat-object JSON reader/writer for the PokéDock BLE protocol (no heap beyond std::string).
// Accepts exactly one object of string / integer / boolean members; rejects nesting, floats,
// duplicate keys, invalid UTF-8 and trailing garbage. Shared by firmware and host tests.
#pragma once
#include <cstdint>
#include <map>
#include <string>

namespace pokedock {

struct JsonValue {
  enum Kind { kString, kInt, kBool } kind = kInt;
  std::string s;
  int64_t i = 0;
  bool b = false;
};
using JsonObject = std::map<std::string, JsonValue>;

inline bool utf8_valid(const std::string &s) {
  size_t i = 0, n = s.size();
  while (i < n) {
    unsigned char c = static_cast<unsigned char>(s[i]);
    int len = c < 0x80 ? 1 : (c >> 5) == 0x6 ? 2 : (c >> 4) == 0xE ? 3 : (c >> 3) == 0x1E ? 4 : 0;
    if (!len || i + len > n) return false;
    uint32_t cp = len == 1 ? c : len == 2 ? (c & 0x1F) : len == 3 ? (c & 0x0F) : (c & 0x07);
    for (int k = 1; k < len; ++k) {
      unsigned char cc = static_cast<unsigned char>(s[i + k]);
      if ((cc >> 6) != 0x2) return false;
      cp = (cp << 6) | (cc & 0x3F);
    }
    if ((len == 2 && cp < 0x80) || (len == 3 && cp < 0x800) || (len == 4 && cp < 0x10000) || cp > 0x10FFFF ||
        (cp >= 0xD800 && cp <= 0xDFFF) || cp < 0x20)
      return false;
    i += len;
  }
  return true;
}

class JsonReader {
 public:
  static bool parse(const std::string &in, JsonObject &out) {
    JsonReader r(in);
    return r.object(out);
  }

 private:
  explicit JsonReader(const std::string &s) : s_(s) {}
  const std::string &s_;
  size_t p_ = 0;
  void ws() {
    while (p_ < s_.size() && (s_[p_] == ' ' || s_[p_] == '\t' || s_[p_] == '\n' || s_[p_] == '\r')) ++p_;
  }
  bool eat(char c) {
    ws();
    if (p_ < s_.size() && s_[p_] == c) {
      ++p_;
      return true;
    }
    return false;
  }
  static void put_utf8(std::string &o, uint32_t cp) {
    if (cp < 0x80) {
      o += char(cp);
    } else if (cp < 0x800) {
      o += char(0xC0 | (cp >> 6));
      o += char(0x80 | (cp & 0x3F));
    } else {
      o += char(0xE0 | (cp >> 12));
      o += char(0x80 | ((cp >> 6) & 0x3F));
      o += char(0x80 | (cp & 0x3F));
    }
  }
  bool string(std::string &o) {
    if (!eat('"')) return false;
    while (p_ < s_.size()) {
      char c = s_[p_++];
      if (c == '"') return utf8_valid(o);
      if (static_cast<unsigned char>(c) < 0x20) return false;
      if (c != '\\') {
        o += c;
        continue;
      }
      if (p_ >= s_.size()) return false;
      char e = s_[p_++];
      switch (e) {
        case '"': o += '"'; break;
        case '\\': o += '\\'; break;
        case '/': o += '/'; break;
        case 'n': o += '\n'; break;
        case 't': o += '\t'; break;
        case 'u': {
          if (p_ + 4 > s_.size()) return false;
          uint32_t cp = 0;
          for (int k = 0; k < 4; ++k) {
            char h = s_[p_++];
            cp <<= 4;
            if (h >= '0' && h <= '9') cp |= uint32_t(h - '0');
            else if (h >= 'a' && h <= 'f') cp |= uint32_t(h - 'a' + 10);
            else if (h >= 'A' && h <= 'F') cp |= uint32_t(h - 'A' + 10);
            else return false;
          }
          if (cp >= 0xD800 && cp <= 0xDFFF) return false;  // no surrogate pairs (BMP only)
          put_utf8(o, cp);
          break;
        }
        default: return false;
      }
    }
    return false;
  }
  bool value(JsonValue &v) {
    ws();
    if (p_ >= s_.size()) return false;
    char c = s_[p_];
    if (c == '"') {
      v.kind = JsonValue::kString;
      return string(v.s);
    }
    if (s_.compare(p_, 4, "true") == 0) {
      v.kind = JsonValue::kBool;
      v.b = true;
      p_ += 4;
      return true;
    }
    if (s_.compare(p_, 5, "false") == 0) {
      v.kind = JsonValue::kBool;
      v.b = false;
      p_ += 5;
      return true;
    }
    bool neg = false;
    if (c == '-') {
      neg = true;
      ++p_;
    }
    size_t start = p_;
    int64_t x = 0;
    while (p_ < s_.size() && s_[p_] >= '0' && s_[p_] <= '9') {
      if (p_ - start >= 15) return false;  // keep inside int64 / JS safe integer
      x = x * 10 + (s_[p_++] - '0');
    }
    if (p_ == start) return false;
    if (p_ < s_.size() && (s_[p_] == '.' || s_[p_] == 'e' || s_[p_] == 'E')) return false;
    v.kind = JsonValue::kInt;
    v.i = neg ? -x : x;
    return true;
  }
  bool object(JsonObject &out) {
    if (!eat('{')) return false;
    if (eat('}')) return trailing();
    do {
      std::string k;
      ws();
      if (!string(k) || !eat(':')) return false;
      JsonValue v;
      if (!value(v)) return false;
      if (!out.emplace(k, v).second) return false;  // duplicate key
    } while (eat(','));
    return eat('}') && trailing();
  }
  bool trailing() {
    ws();
    return p_ == s_.size();
  }
};

class JsonWriter {
 public:
  JsonWriter &kv(const char *k, int64_t v) {
    key(k);
    out_ += std::to_string(v);
    return *this;
  }
  JsonWriter &kv(const char *k, const std::string &v) {
    key(k);
    out_ += '"';
    for (char c : v) {
      if (c == '"' || c == '\\') out_ += '\\';
      if (c == '\n') {
        out_ += "\\n";
        continue;
      }
      out_ += c;
    }
    out_ += '"';
    return *this;
  }
  JsonWriter &raw(const char *k, const std::string &json) {
    key(k);
    out_ += json;
    return *this;
  }
  std::string str() const { return out_ + "}"; }

 private:
  void key(const char *k) {
    out_ += first_ ? "" : ",";
    first_ = false;
    out_ += '"';
    out_ += k;
    out_ += "\":";
  }
  std::string out_ = "{";
  bool first_ = true;
};

}  // namespace pokedock
