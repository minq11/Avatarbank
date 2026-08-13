<template>
  <!--
    아바타 썸네일. 고르는 화면(스튜디오·직접 만들기)과 고정된 화면(리딤 링크)에서
    같은 규격으로 쓰려고 원시 값만 받는다 — AvatarItem 을 못 가진 쪽도 쓸 수 있게.
    같은 폼의 참조 이미지 썸네일(.source-thumb)과 크기·모양이 같아야 정렬선이 맞는다.
  -->
  <div class="pick-thumb" :class="{ empty: !title }">
    <img v-if="previewUrl" :src="previewUrl" :alt="title || ''" />
    <span v-else-if="title" class="pick-initial">{{ initial }}</span>
    <span v-else class="pick-placeholder" aria-hidden="true">👤</span>

    <span v-if="hidden" class="pick-badge">비공개</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    /** 아바타 이름. 없으면 "아직 안 고름" 상태로 그린다. */
    title?: string | null;
    previewUrl?: string | null;
    /** 비공개 아바타임을 알리는 뱃지 */
    hidden?: boolean;
  }>(),
  { title: null, previewUrl: null, hidden: false }
);

/** 미리보기 이미지가 없을 때 대신 보여줄 머리글자. */
const initial = computed(() => props.title?.trim().charAt(0) || "?");
</script>

<style scoped>
.pick-thumb {
  position: relative;
  flex-shrink: 0;
  width: 140px;
  height: 176px;
  border-radius: 0.7rem;
  border: 1px solid #e6e6ea;
  background: #fafafa;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 선택 전에도 자리를 유지해 고르는 순간 레이아웃이 튀지 않게 */
.pick-thumb.empty {
  border-style: dashed;
  background: transparent;
}

.pick-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.pick-initial {
  font-size: 2.8rem;
  font-weight: 800;
  color: #c24210;
}

.pick-placeholder {
  font-size: 2.4rem;
  opacity: 0.35;
}

/* 참조 이미지 썸네일의 "기본" 뱃지와 같은 형태 */
.pick-badge {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(17, 24, 39, 0.72);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  padding: 0.22rem 0;
  text-align: center;
}
</style>
