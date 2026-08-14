/**
 * Avatar preview image: 1) frontend assets/preview_image/{id}.* 2) API /static/preview_image/{id}.png 3) S3
 */

// 개발·운영 모두 같은 오리진의 /api 를 거친다 (services/api.ts 주석 참고).
const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

// Build-time: avatar id -> asset URL (from frontend/src/assets/preview_image/*)
const assetMap: Record<number, string> = {};
const glob = import.meta.glob<string>("@/assets/preview_image/*", {
  eager: true,
  as: "url",
});
for (const path of Object.keys(glob)) {
  const match = path.match(/preview_image\/(\d+)(\.\w+)?$/);
  if (match) {
    const id = parseInt(match[1], 10);
    if (!Number.isNaN(id) && glob[path]) {
      assetMap[id] = glob[path];
    }
  }
}

function resolveS3Url(s3Path: string | null | undefined): string {
  if (!s3Path) return "";
  if (s3Path.startsWith("http://") || s3Path.startsWith("https://")) return s3Path;
  return API_BASE + (s3Path.startsWith("/") ? s3Path : "/" + s3Path);
}

// 1x1 transparent PNG – preview 없을 때 서버 요청 없이 사용
const EMPTY_PREVIEW_DATA_URI =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";

/**
 * Returns { primary, fallback } for avatar preview.
 * Use primary as img src; on error set src to fallback.
 * preview_image_url이 없으면 /static/preview_image/{id}.png를 요청하지 않고 빈 이미지 데이터 URI를 씀.
 */
export function getAvatarPreviewUrls(
  avatarId: number,
  s3PreviewPath: string | null | undefined
): { primary: string; fallback: string } {
  const hasS3 = !!s3PreviewPath?.trim();
  const s3Url = resolveS3Url(s3PreviewPath);
  const fromAsset = assetMap[avatarId];

  if (fromAsset) {
    return { primary: fromAsset, fallback: s3Url || fromAsset };
  }
  if (hasS3) {
    return { primary: s3Url, fallback: s3Url };
  }
  // preview 없음: /static/preview_image/{id}.png 요청하지 않음 (404 무한 재시도 방지)
  return { primary: EMPTY_PREVIEW_DATA_URI, fallback: EMPTY_PREVIEW_DATA_URI };
}
