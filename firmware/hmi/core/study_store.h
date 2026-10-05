#pragma once
#include "models.h"
#include "study_engine.h"

class StudyStore {
 public:
  virtual ~StudyStore() = default;

  virtual bool loadDailyStats(const char* yyyymmdd, DailyStudyStats& out) = 0;
  virtual bool saveDailyStats(const char* yyyymmdd, const DailyStudyStats& stats) = 0;

  virtual int loadTodos(TodoItem out[POKEDOCK_MAX_TODOS]) = 0;
  virtual bool saveTodos(const TodoItem items[POKEDOCK_MAX_TODOS], int count) = 0;

  virtual bool appendFocusSession(uint32_t started_epoch,
                                  uint32_t duration_s,
                                  uint16_t pokemon_id) = 0;
};

// Recommended implementation:
// - NVS: small settings / today summary / recovery state
// - microSD: append-only session history and larger assets
// Never persist phone notification contents.
