<template>
  <div ref="rootRef" class="searchable-select">
    <button
      type="button"
      class="searchable-select-trigger"
      :class="{ open: isOpen, placeholder: !selectedLabel }"
      @click="toggleOpen"
    >
      <span class="trigger-text">{{ selectedLabel || placeholder }}</span>
      <span class="trigger-arrow">▼</span>
    </button>

    <Transition name="dropdown">
      <div v-show="isOpen" class="searchable-select-dropdown">
        <input
          ref="searchInputRef"
          v-model="searchQuery"
          type="text"
          class="searchable-select-search"
          placeholder="Search..."
          @keydown.escape="close"
          @keydown.down.prevent="focusNext"
          @keydown.up.prevent="focusPrev"
          @keydown.enter.prevent="selectFocused"
        />
        <ul ref="listRef" class="searchable-select-list" role="listbox">
          <li
            v-for="(opt, index) in filteredOptions"
            :key="opt.value"
            class="searchable-select-option"
            :class="{ focused: focusedIndex === index, selected: modelValue === opt.value }"
            role="option"
            :aria-selected="modelValue === opt.value"
            @click="select(opt.value)"
            @mouseenter="focusedIndex = index"
          >
            {{ opt.label }}
          </li>
          <li v-if="filteredOptions.length === 0" class="searchable-select-empty">
            No matches
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";

export interface SearchableOption {
  value: number | string;
  label: string;
  /** 검색 시 사용할 텍스트. 없으면 label로 검색 (예: label에 "C"가 들어가면 C 검색 시 전부 노출되므로 searchText로 제목만 넣기) */
  searchText?: string;
}

const props = withDefaults(
  defineProps<{
    modelValue: number | string | "";
    options: SearchableOption[];
    placeholder?: string;
  }>(),
  { placeholder: "— Select —" }
);

const emit = defineEmits<{
  "update:modelValue": [value: number | string | ""];
}>();

const rootRef = ref<HTMLElement | null>(null);
const searchInputRef = ref<HTMLInputElement | null>(null);
const listRef = ref<HTMLElement | null>(null);
const isOpen = ref(false);
const searchQuery = ref("");
const focusedIndex = ref(0);

const selectedLabel = computed(() => {
  if (props.modelValue === "" || props.modelValue == null) return "";
  const opt = props.options.find((o) => o.value === props.modelValue);
  return opt ? opt.label : "";
});

const filteredOptions = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return props.options;
  return props.options.filter((o) => {
    const text = (o.searchText ?? o.label).toLowerCase();
    return text.includes(q);
  });
});

function toggleOpen() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    searchQuery.value = "";
    focusedIndex.value = 0;
    requestAnimationFrame(() => {
      searchInputRef.value?.focus();
    });
  }
}

function close() {
  isOpen.value = false;
}

function select(value: number | string) {
  emit("update:modelValue", value);
  close();
}

function focusNext() {
  focusedIndex.value = Math.min(focusedIndex.value + 1, filteredOptions.value.length - 1);
}

function focusPrev() {
  focusedIndex.value = Math.max(focusedIndex.value - 1, 0);
}

function selectFocused() {
  const opts = filteredOptions.value;
  if (opts[focusedIndex.value]) {
    select(opts[focusedIndex.value].value);
  }
}

watch(isOpen, (open) => {
  if (!open) return;
  focusedIndex.value = filteredOptions.value.findIndex((o) => o.value === props.modelValue);
  if (focusedIndex.value < 0) focusedIndex.value = 0;
});

// Click outside to close
function onDocClick(e: MouseEvent) {
  if (rootRef.value && !rootRef.value.contains(e.target as Node)) {
    close();
  }
}

watch(isOpen, (open) => {
  if (open) {
    setTimeout(() => document.addEventListener("click", onDocClick), 0);
  } else {
    document.removeEventListener("click", onDocClick);
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
});
</script>

<style scoped>
.searchable-select {
  position: relative;
  width: 100%;
}

.searchable-select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  font-size: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  background: #fff;
  color: #111827;
  cursor: pointer;
  text-align: left;
}

.searchable-select-trigger.placeholder {
  color: #9ca3af;
}

.searchable-select-trigger.open {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.searchable-select-trigger .trigger-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.searchable-select-trigger .trigger-arrow {
  flex-shrink: 0;
  margin-left: 0.5rem;
  font-size: 0.65rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.searchable-select-trigger.open .trigger-arrow {
  transform: rotate(180deg);
}

.searchable-select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 50;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.searchable-select-search {
  width: 100%;
  padding: 0.6rem 0.85rem;
  font-size: 0.95rem;
  border: none;
  border-bottom: 1px solid #e5e7eb;
  outline: none;
}

.searchable-select-search::placeholder {
  color: #9ca3af;
}

.searchable-select-list {
  max-height: 220px;
  overflow-y: auto;
  margin: 0;
  padding: 0.25rem 0;
  list-style: none;
}

.searchable-select-option {
  padding: 0.55rem 0.85rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.15s;
}

.searchable-select-option:hover,
.searchable-select-option.focused {
  background: #f3f4f6;
}

.searchable-select-option.selected {
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 500;
}

.searchable-select-empty {
  padding: 0.75rem 0.85rem;
  font-size: 0.9rem;
  color: #9ca3af;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
