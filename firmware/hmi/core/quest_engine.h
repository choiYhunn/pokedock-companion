#pragma once
#include <stdint.h>

struct QuestProgress {
  uint8_t focus_sessions=0; uint8_t focus_goal=3;
  uint16_t focus_minutes=0; uint16_t focus_minutes_goal=180;
  uint8_t todos_done=0; uint8_t todos_goal=3;
};

inline bool daily_focus_quest_complete(const QuestProgress& q){return q.focus_sessions>=q.focus_goal;}
inline bool daily_minutes_quest_complete(const QuestProgress& q){return q.focus_minutes>=q.focus_minutes_goal;}
inline bool daily_todo_quest_complete(const QuestProgress& q){return q.todos_done>=q.todos_goal;}
inline void quest_apply_focus(QuestProgress& q,uint16_t minutes){
  if(q.focus_sessions<255u) q.focus_sessions++;
  const uint32_t total=static_cast<uint32_t>(q.focus_minutes)+minutes;
  q.focus_minutes=static_cast<uint16_t>(total>65535u?65535u:total);
}
