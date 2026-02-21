/**
 * Avatar preview image: 1) frontend assets/preview_image/{id}.* 2) API /static/preview_image/{id}.png 3) S3
 */

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "/api" : "http://localhost:8000");

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

/**
 * Returns { primary, fallback } for avatar preview.
 * Use primary as img src; on error set src to fallback.
 */
export function getAvatarPreviewUrls(
  avatarId: number,
  s3PreviewPath: string | null | undefined
): { primary: string; fallback: string } {
  const fallback = resolveS3Url(s3PreviewPath);
  const primary =
    assetMap[avatarId] ??
    (avatarId ? `${API_BASE}/static/preview_image/${avatarId}.png` : fallback);
  return { primary, fallback: fallback || primary };
}
