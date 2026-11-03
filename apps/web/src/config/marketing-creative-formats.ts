/**
 * Marketing creative format catalog — target print/social dimensions.
 * OpenAI Images only accepts 1024x1024 | 1024x1536 | 1536x1024; we map
 * each creative to the nearest generation size and keep target specs for
 * Canva / export / prompt guidance.
 */

export type OpenAiImageSize = "1024x1024" | "1024x1536" | "1536x1024";

export type CreativeCategoryId =
  | "social"
  | "stationery"
  | "print"
  | "event_backdrop"
  | "event_flex";

export type CreativeFormat = {
  id: string;
  label: string;
  /** Target output pixels (W × H). */
  widthPx: number;
  heightPx: number;
  inches: string;
  cms: string;
  /** OpenAI generation size (nearest aspect). */
  openaiSize: OpenAiImageSize;
  /** Suggested quality default for this use case. */
  suggestedQuality: "low" | "medium" | "high" | "xhigh";
  /** Short platform / channel tag stored on the post. */
  platformTag: string;
};

export type CreativeCategory = {
  id: CreativeCategoryId;
  label: string;
  description: string;
  formats: CreativeFormat[];
};

function openaiSizeFor(w: number, h: number): OpenAiImageSize {
  const aspect = w / h;
  if (Math.abs(aspect - 1) <= 0.12) return "1024x1024";
  if (aspect < 1) return "1024x1536";
  return "1536x1024";
}

function fmt(
  id: string,
  label: string,
  widthPx: number,
  heightPx: number,
  inches: string,
  cms: string,
  platformTag: string,
  suggestedQuality: CreativeFormat["suggestedQuality"] = "medium",
): CreativeFormat {
  return {
    id,
    label,
    widthPx,
    heightPx,
    inches,
    cms,
    openaiSize: openaiSizeFor(widthPx, heightPx),
    suggestedQuality,
    platformTag,
  };
}

export const CREATIVE_CATEGORIES: CreativeCategory[] = [
  {
    id: "social",
    label: "Social media creatives",
    description: "Feed, story, cover, and thumbnail sizes for major networks.",
    formats: [
      fmt("ig_post", "Instagram Post", 1080, 1080, "3.6 × 3.6 in @300 DPI", "9.14 × 9.14 cm", "instagram", "low"),
      fmt("ig_portrait", "Instagram Portrait", 1080, 1350, "3.6 × 4.5 in", "9.14 × 11.43 cm", "instagram", "low"),
      fmt("ig_story", "Instagram Story", 1080, 1920, "3.6 × 6.4 in", "9.14 × 16.26 cm", "instagram", "low"),
      fmt("fb_post", "Facebook Post", 1200, 630, "4 × 2.1 in", "10.16 × 5.33 cm", "facebook", "low"),
      fmt("fb_cover", "Facebook Cover", 1640, 624, "5.47 × 2.08 in", "13.89 × 5.28 cm", "facebook", "low"),
      fmt("li_post", "LinkedIn Post", 1200, 1200, "4 × 4 in", "10.16 × 10.16 cm", "linkedin", "medium"),
      fmt("li_banner", "LinkedIn Banner", 1584, 396, "5.28 × 1.32 in", "13.41 × 3.35 cm", "linkedin", "medium"),
      fmt("x_post", "X (Twitter) Post", 1600, 900, "5.33 × 3 in", "13.55 × 7.62 cm", "twitter", "low"),
      fmt("yt_thumb", "YouTube Thumbnail", 1280, 720, "4.27 × 2.4 in", "10.84 × 6.10 cm", "youtube", "medium"),
      fmt("wa_status", "WhatsApp Status", 1080, 1920, "3.6 × 6.4 in", "9.14 × 16.26 cm", "whatsapp", "low"),
    ],
  },
  {
    id: "stationery",
    label: "Corporate stationery",
    description: "Letterhead, cards, envelopes, and ID — print-ready targets.",
    formats: [
      fmt("letterhead", "Letterhead", 2480, 3508, "8.27 × 11.69 in", "21 × 29.7 cm", "stationery", "high"),
      fmt("business_card", "Business Card", 1050, 600, "3.5 × 2 in", "8.89 × 5.08 cm", "stationery", "high"),
      fmt("dl_envelope", "DL Envelope", 2598, 1299, "8.66 × 4.33 in", "22 × 11 cm", "stationery", "high"),
      fmt("c5_envelope", "C5 Envelope", 2706, 1914, "9.02 × 6.38 in", "22.9 × 16.2 cm", "stationery", "high"),
      fmt("id_card", "ID Card", 1013, 638, "3.375 × 2.125 in", "8.56 × 5.40 cm", "stationery", "high"),
    ],
  },
  {
    id: "print",
    label: "Brochures & print collateral",
    description: "Folded brochures, flyers, and presentation folders.",
    formats: [
      fmt("bifold", "Bi-Fold Brochure", 2480, 3508, "8.27 × 11.69 in", "21 × 29.7 cm", "print", "high"),
      fmt("trifold", "Tri-Fold Brochure", 3508, 2480, "11.69 × 8.27 in", "29.7 × 21 cm", "print", "high"),
      fmt("a4_flyer", "A4 Flyer", 1748, 2480, "5.83 × 8.27 in", "14.8 × 21 cm", "print", "high"),
      fmt("a5_flyer", "A5 Flyer", 2480, 3508, "8.27 × 11.69 in", "21 × 29.7 cm", "print", "high"),
      fmt("pres_folder", "Presentation Folder", 5400, 3600, "18 × 12 in", "45.72 × 30.48 cm", "print", "high"),
    ],
  },
  {
    id: "event_backdrop",
    label: "Event branding — backdrops & standees",
    description: "Registration / stage backdrops, standees, podium wraps.",
    formats: [
      fmt("reg_8x8", "Registration Backdrop (8 × 8 ft)", 14400, 14400, "96 × 96 in", "243.8 × 243.8 cm", "event", "xhigh"),
      fmt("reg_10x8", "Registration Backdrop (10 × 8 ft)", 18000, 14400, "120 × 96 in", "304.8 × 243.8 cm", "event", "xhigh"),
      fmt("reg_12x8", "Registration Backdrop (12 × 8 ft)", 21600, 14400, "144 × 96 in", "365.8 × 243.8 cm", "event", "xhigh"),
      fmt("stage_20x10", "Stage Backdrop (20 × 10 ft)", 36000, 18000, "240 × 120 in", "609.6 × 304.8 cm", "event", "xhigh"),
      fmt("stage_24x12", "Stage Backdrop (24 × 12 ft)", 43200, 21600, "288 × 144 in", "731.5 × 365.8 cm", "event", "xhigh"),
      fmt("stage_30x10", "Stage Backdrop (30 × 10 ft)", 54000, 18000, "360 × 120 in", "914.4 × 304.8 cm", "event", "xhigh"),
      fmt("standee_2x5", "Standee (2 × 5 ft)", 3600, 9000, "24 × 60 in", "60.96 × 152.4 cm", "event", "high"),
      fmt("standee_2_5x6", "Standee (2.5 × 6 ft)", 4500, 10800, "30 × 72 in", "76.2 × 182.9 cm", "event", "high"),
      fmt("standee_3x6", "Standee (3 × 6 ft)", 5400, 10800, "36 × 72 in", "91.4 × 182.9 cm", "event", "high"),
      fmt("podium_2x3", "Podium Branding (2 × 3 ft)", 3600, 5400, "24 × 36 in", "60.96 × 91.44 cm", "event", "high"),
    ],
  },
  {
    id: "event_flex",
    label: "Event branding — horizontal flex",
    description: "Large-format horizontal flex banners for venues and outdoors.",
    formats: [
      fmt("flex_6x3", "Horizontal Flex (6 × 3 ft)", 10800, 5400, "72 × 36 in", "182.9 × 91.4 cm", "event", "xhigh"),
      fmt("flex_8x4", "Horizontal Flex (8 × 4 ft)", 14400, 7200, "96 × 48 in", "243.8 × 121.9 cm", "event", "xhigh"),
      fmt("flex_10x5", "Horizontal Flex (10 × 5 ft)", 18000, 9000, "120 × 60 in", "304.8 × 152.4 cm", "event", "xhigh"),
    ],
  },
];

export function getCategory(id: CreativeCategoryId): CreativeCategory {
  return CREATIVE_CATEGORIES.find((c) => c.id === id) ?? CREATIVE_CATEGORIES[0];
}

export function getFormat(categoryId: CreativeCategoryId, formatId: string): CreativeFormat {
  const cat = getCategory(categoryId);
  return cat.formats.find((f) => f.id === formatId) ?? cat.formats[0];
}

export function pixelsLabel(format: CreativeFormat): string {
  return `${format.widthPx.toLocaleString("en-IN")} × ${format.heightPx.toLocaleString("en-IN")} px`;
}

export function openaiSizeLabel(size: OpenAiImageSize): string {
  switch (size) {
    case "1024x1024":
      return "Square 1:1 (1024×1024)";
    case "1024x1536":
      return "Portrait 2:3 (1024×1536)";
    case "1536x1024":
      return "Landscape 3:2 (1536×1024)";
  }
}

/** Prompt suffix so the model composes for the real deliverable crop. */
export function creativePromptHint(format: CreativeFormat, categoryLabel: string): string {
  return [
    `Deliverable: ${format.label} (${categoryLabel}).`,
    `Compose for final crop ${format.widthPx}×${format.heightPx}px (${format.inches}; ${format.cms}).`,
    "Keep critical text and logo clear of edges; leave safe margins for print/bleed where relevant.",
  ].join(" ");
}
