import datetime
import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image
from huggingface_hub import InferenceClient


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
HF_TOKEN = os.environ["HF_TOKEN"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


# ============================================================
# TELEGRAM CHANNEL
# ============================================================

CHANNEL = "@BHUVIAIPROMPTIMAGES"


# ============================================================
# TIMEZONE
# ============================================================

IST = datetime.timezone(
    datetime.timedelta(hours=5, minutes=30)
)


# ============================================================
# CONTROLLED CONTENT CATEGORIES
# ============================================================

CATEGORIES = [
    {
        "id": "cinematic_photography",
        "name": "Cinematic Photography",
        "description": (
            "Realistic cinematic photography, portraits, streets, "
            "environments and dramatic scenes."
        ),
        "rules": (
            "Prioritize believable photography, natural materials, "
            "strong composition, realistic skin and environmental detail."
        ),
    },
    {
        "id": "game_art",
        "name": "Game Art",
        "description": (
            "Game development concepts, characters, environments, "
            "worlds and cinematic game scenes."
        ),
        "rules": (
            "Prioritize worldbuilding, environmental storytelling, "
            "game-ready visual design and cinematic composition."
        ),
    },
    {
        "id": "cyberpunk",
        "name": "Cyberpunk",
        "description": (
            "Futuristic cities, technology, programmers, neon "
            "environments and cyberpunk storytelling."
        ),
        "rules": (
            "Prioritize neon atmosphere, believable futuristic technology, "
            "rain, reflections, controlled contrast and layered depth."
        ),
    },
    {
        "id": "sci_fi",
        "name": "Science Fiction",
        "description": (
            "Advanced technology, spacecraft, laboratories, "
            "futuristic worlds and speculative environments."
        ),
        "rules": (
            "Prioritize believable futuristic engineering, scale, "
            "materials, atmospheric perspective and scientific detail."
        ),
    },
    {
        "id": "fantasy",
        "name": "Fantasy",
        "description": (
            "Epic fantasy environments, characters, magical worlds "
            "and cinematic storytelling."
        ),
        "rules": (
            "Prioritize believable fantasy materials, environmental "
            "storytelling, dramatic lighting and coherent worldbuilding."
        ),
    },
    {
        "id": "product_visuals",
        "name": "Product Visuals",
        "description": (
            "Premium product photography, advertising concepts, "
            "commercial visuals and studio scenes."
        ),
        "rules": (
            "Prioritize premium commercial composition, realistic "
            "materials, controlled studio lighting and clean backgrounds."
        ),
    },
    {
        "id": "architecture",
        "name": "Architecture",
        "description": (
            "Modern architecture, futuristic buildings, interiors, "
            "urban spaces and architectural photography."
        ),
        "rules": (
            "Prioritize structural accuracy, perspective, realistic "
            "materials, scale and architectural photography."
        ),
    },
    {
        "id": "surreal_art",
        "name": "Surreal Art",
        "description": (
            "Dreamlike, imaginative, unusual and visually striking "
            "conceptual scenes."
        ),
        "rules": (
            "Prioritize one strong surreal idea, visual clarity, "
            "coherent impossible elements and deliberate composition."
        ),
    },
]


# ============================================================
# WEEKLY THEMES
# ============================================================

WEEKLY_THEMES = [
    "Visual Storytelling",
    "Future Worlds",
    "Cinematic Moments",
    "Extreme Environments",
    "Human + Technology",
    "Dream Worlds",
    "Premium Visual Design",
]


# ============================================================
# PERMANENT VISUAL IDENTITY
# ============================================================

STYLE = """
Maintain a premium, cinematic and professional visual identity.

Use strong visual storytelling.

Prefer realistic materials and believable environments.

Use sophisticated composition and deliberate camera perspective.

Use detailed textures and atmospheric depth.

Use strong but controlled contrast.

Use cinematic lighting appropriate to the scene.

Use physically believable light behavior.

Avoid cheap-looking AI aesthetics.

Avoid generic stock-photo composition.

Avoid excessive visual clutter.

Avoid unnecessary objects.

Avoid visible text unless the concept absolutely requires it.

Avoid watermarks.

Avoid logos.

Avoid random letters.

Avoid distorted anatomy.

Avoid malformed hands.

Avoid extra fingers.

Avoid duplicated people.

Avoid duplicated objects.

Avoid impossible geometry.

Keep the subject visually coherent.

Every image must feel intentionally designed rather than randomly generated.
"""


# ============================================================
# CATEGORY-SPECIFIC NEGATIVE RULES
# ============================================================

NEGATIVE_RULES = {
    "cinematic_photography": (
        "plastic skin, oversharpening, fake HDR, unnatural face, "
        "bad anatomy, duplicate subjects"
    ),
    "game_art": (
        "generic game asset, unfinished concept, broken anatomy, "
        "random UI, floating objects, inconsistent perspective"
    ),
    "cyberpunk": (
        "random text, fake logos, excessive neon, muddy shadows, "
        "duplicate signs, broken architecture"
    ),
    "sci_fi": (
        "toy-like machinery, impossible engineering, random text, "
        "floating components, broken perspective"
    ),
    "fantasy": (
        "cheap fantasy art, plastic materials, malformed anatomy, "
        "random glowing objects, visual clutter"
    ),
    "product_visuals": (
        "cheap advertising, distorted product, fake logo, random text, "
        "scratches unless intentional, messy background"
    ),
    "architecture": (
        "warped buildings, impossible geometry, crooked verticals, "
        "duplicate windows, distorted perspective"
    ),
    "surreal_art": (
        "random clutter, incoherent objects, accidental distortion, "
        "unintentional text, malformed anatomy"
    ),
}


# ============================================================
# DAILY CATEGORY / THEME
# ============================================================

now = datetime.datetime.now(IST)

day_number = now.timetuple().tm_yday

slot = 0 if now.hour < 15 else 1

category_index = (
    ((day_number - 1) * 2) + slot
) % len(CATEGORIES)

category = CATEGORIES[category_index]

weekly_theme = WEEKLY_THEMES[
    (day_number // 7) % len(WEEKLY_THEMES)
]


# ============================================================
# GEMINI PROMPT ENGINE
# ============================================================

PROMPT_REQUEST = f"""
You are the advanced content engine for a professional AI image prompt library.

The goal is NOT to create random pretty images.

The goal is to create useful, original, copy-ready AI image prompts
that teach people how to create strong images.

Today's category:

{category["name"]}

Category description:

{category["description"]}

Category-specific rules:

{category["rules"]}

Weekly theme:

{weekly_theme}

Permanent visual identity:

{STYLE}

Create EXACTLY 4 different image concepts.

The four concepts must feel like one premium collection,
but must be substantially different from one another.

Do NOT create four variations of the same scene.

Each image must have a different:

- subject
- environment
- action
- composition
- camera perspective
- visual story

Make every concept independently useful.

For EACH image return:

1. concept_title
2. subject
3. style
4. composition
5. lighting
6. camera
7. modifiers
8. aspect_ratio
9. full_prompt
10. breakdown
11. difficulty

Difficulty must be exactly one of:

"Beginner"
"Intermediate"
"Advanced"

Aspect ratio must be exactly one of:

"1:1"
"4:5"
"16:9"
"9:16"

Use:

4:5 for portraits, editorial and social imagery.

9:16 for vertical cinematic scenes.

16:9 for landscapes, environments and cinematic wide scenes.

1:1 for balanced square artwork and product compositions.

The full_prompt must contain:

- subject
- appearance
- pose/action
- clothing when relevant
- environment
- background
- foreground
- composition
- perspective
- lighting
- atmosphere
- color palette
- camera
- lens
- depth of field
- materials
- textures
- fine details
- cinematic mood
- quality instructions
- negative instructions

Make the prompt detailed but not repetitive.

Do not add explanations inside full_prompt.

Do not copy prompts from websites.

Do not mention OpenArt, PromptCreek, Reddit, Midjourney,
Flux, Stable Diffusion or any other external source.

Do not claim that a prompt was tested on any particular model.

The breakdown must contain EXACTLY 3 short educational explanations.

Each explanation should teach why a prompt element improves the image.

Example:

"85mm lens → creates natural portrait compression."

"Rim lighting → separates the subject from the background."

"Shallow depth of field → directs attention to the subject."

Return ONLY valid JSON.

EXACT STRUCTURE:

{{
  "collection_title": "short memorable collection title",
  "collection_description": "2 short useful sentences",
  "images": [
    {{
      "concept_title": "title",
      "subject": "subject",
      "style": "style",
      "composition": "composition",
      "lighting": "lighting",
      "camera": "camera",
      "modifiers": "modifiers",
      "aspect_ratio": "16:9",
      "difficulty": "Advanced",
      "full_prompt": "complete copy-ready prompt",
      "breakdown": [
        "explanation 1",
        "explanation 2",
        "explanation 3"
      ]
    }},
    {{
      "concept_title": "title",
      "subject": "subject",
      "style": "style",
      "composition": "composition",
      "lighting": "lighting",
      "camera": "camera",
      "modifiers": "modifiers",
      "aspect_ratio": "4:5",
      "difficulty": "Intermediate",
      "full_prompt": "complete copy-ready prompt",
      "breakdown": [
        "explanation 1",
        "explanation 2",
        "explanation 3"
      ]
    }},
    {{
      "concept_title": "title",
      "subject": "subject",
      "style": "style",
      "composition": "composition",
      "lighting": "lighting",
      "camera": "camera",
      "modifiers": "modifiers",
      "aspect_ratio": "16:9",
      "difficulty": "Advanced",
      "full_prompt": "complete copy-ready prompt",
      "breakdown": [
        "explanation 1",
        "explanation 2",
        "explanation 3"
      ]
    }},
    {{
      "concept_title": "title",
      "subject": "subject",
      "style": "style",
      "composition": "composition",
      "lighting": "lighting",
      "camera": "camera",
      "modifiers": "modifiers",
      "aspect_ratio": "9:16",
      "difficulty": "Beginner",
      "full_prompt": "complete copy-ready prompt",
      "breakdown": [
        "explanation 1",
        "explanation 2",
        "explanation 3"
      ]
    }}
  ]
}}
"""


# ============================================================
# GEMINI API
# ============================================================

def gemini_request():

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash:generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": PROMPT_REQUEST
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_KEY,
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=120,
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def extract_gemini_text(result):

    try:

        return (
            result["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except (KeyError, IndexError, TypeError) as error:

        print("Unexpected Gemini response:")

        print(
            json.dumps(
                result,
                indent=2,
            )[:5000]
        )

        raise Exception(
            "Gemini response did not contain valid text."
        ) from error


# ============================================================
# VALIDATION
# ============================================================

def validate_result(result):

    if not isinstance(result, dict):
        raise ValueError(
            "Gemini result is not an object."
        )

    images = result.get("images")

    if not isinstance(images, list):
        raise ValueError(
            "Missing images list."
        )

    if len(images) != 4:
        raise ValueError(
            f"Expected exactly 4 images, got {len(images)}."
        )

    if not result.get("collection_title"):
        raise ValueError(
            "Missing collection_title."
        )

    valid_ratios = {
        "1:1",
        "4:5",
        "16:9",
        "9:16",
    }

    valid_difficulty = {
        "Beginner",
        "Intermediate",
        "Advanced",
    }

    required_fields = [
        "concept_title",
        "subject",
        "style",
        "composition",
        "lighting",
        "camera",
        "modifiers",
        "aspect_ratio",
        "difficulty",
        "full_prompt",
        "breakdown",
    ]

    for index, image in enumerate(
        images,
        start=1,
    ):

        if not isinstance(image, dict):
            raise ValueError(
                f"Image {index} is not an object."
            )

        for field in required_fields:

            if not image.get(field):
                raise ValueError(
                    f"Image {index} missing '{field}'."
                )

        if image["aspect_ratio"] not in valid_ratios:

            raise ValueError(
                f"Image {index} has invalid aspect ratio."
            )

        if image["difficulty"] not in valid_difficulty:

            raise ValueError(
                f"Image {index} has invalid difficulty."
            )

        if not isinstance(
            image["breakdown"],
            list,
        ):

            raise ValueError(
                f"Image {index} breakdown is invalid."
            )

        if len(image["breakdown"]) != 3:

            raise ValueError(
                f"Image {index} must have exactly 3 breakdown points."
            )

    return result


# ============================================================
# PROMPT QUALITY SCORING
# ============================================================

def score_prompt(prompt):

    score = 0

    checks = [
        ("subject", 1),
        ("lighting", 1),
        ("camera", 1),
        ("lens", 1),
        ("composition", 1),
        ("depth of field", 1),
        ("texture", 1),
        ("atmosphere", 1),
        ("foreground", 1),
        ("background", 1),
        ("materials", 1),
        ("color", 1),
    ]

    prompt_lower = prompt.lower()

    for keyword, points in checks:

        if keyword in prompt_lower:
            score += points

    if len(prompt) >= 700:
        score += 1

    if len(prompt) >= 1100:
        score += 1

    return min(score, 14)


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def prompt_fingerprint(prompt):

    normalized = " ".join(
        prompt.lower().split()
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


# ============================================================
# ASPECT RATIO → IMAGE SIZE
# ============================================================

def get_dimensions(aspect_ratio):

    dimensions = {
        "1:1": (1024, 1024),
        "4:5": (1024, 1280),
        "16:9": (1536, 864),
        "9:16": (864, 1536),
    }

    return dimensions.get(
        aspect_ratio,
        (1024, 1024),
    )


# ============================================================
# CATEGORY-SPECIFIC NEGATIVE PROMPT
# ============================================================

def get_negative_prompt():

    return NEGATIVE_RULES.get(
        category["id"],
        (
            "low quality, blurry, distorted anatomy, "
            "duplicate objects, random text, watermark"
        ),
    )


# ============================================================
# BUILD FINAL IMAGE PROMPT
# ============================================================

def build_image_prompt(image):

    negative = get_negative_prompt()

    return f"""
{image["full_prompt"]}

QUALITY DIRECTION:
Premium visual quality, coherent details, realistic materials,
physically believable lighting, controlled contrast,
strong subject separation, professional composition,
natural texture, atmospheric depth, high detail.

NEGATIVE DIRECTION:
{negative}

Do not include watermarks, random letters, random logos,
unwanted text, malformed anatomy, extra fingers, duplicated
subjects, duplicated objects, broken geometry, or accidental
visual artifacts.
""".strip()


# ============================================================
# POLLINATIONS IMAGE GENERATION
# ============================================================

def download_image(
    prompt,
    filename,
    aspect_ratio="1:1",
):

    width, height = get_dimensions(
        aspect_ratio
    )

    final_prompt = urllib.parse.quote(
        prompt
    )

    url = (
        "https://image.pollinations.ai/prompt/"
        f"{final_prompt}"
        f"?width={width}"
        f"&height={height}"
        "&nologo=true"
    )

    max_attempts = 3

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        print(
            f"Image generation attempt "
            f"{attempt}/{max_attempts}"
        )

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
            )

            with urllib.request.urlopen(
                request,
                timeout=180,
            ) as response:

                image_data = response.read()

            if len(image_data) < 10_000:

                raise ValueError(
                    "Generated image file is suspiciously small."
                )

            with open(
                filename,
                "wb",
            ) as file:

                file.write(image_data)

            validate_image(
                filename,
                width,
                height,
            )

            print(
                f"Saved image: {filename}"
            )

            return filename

        except Exception as error:

            print(
                f"Image generation failed: {error}"
            )

            if attempt < max_attempts:

                wait_time = 5 * attempt

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

    raise Exception(
        f"Failed to generate {filename} "
        f"after {max_attempts} attempts."
    )


# ============================================================
# IMAGE VALIDATION
# ============================================================

def validate_image(
    filename,
    requested_width,
    requested_height,
):

    try:

        with Image.open(
            filename
        ) as image:

            width, height = image.size

            print(
                f"Image validated: "
                f"{width}x{height}"
            )

            if width < 512 or height < 512:

                raise ValueError(
                    "Generated image resolution is too low."
                )

            image.verify()

    except Exception as error:

        if os.path.exists(filename):
            os.remove(filename)

        raise ValueError(
            f"Invalid generated image: {error}"
        )


# ============================================================
# GEMINI CONTENT GENERATION
# ============================================================

def gemini_generate_content():

    last_error = None

    for attempt in range(
        1,
        3,
    ):

        print(
            f"Gemini generation attempt "
            f"{attempt}/2..."
        )

        try:

            raw_result = gemini_request()

            text = extract_gemini_text(
                raw_result
            )

            result = json.loads(
                text
            )

            result = validate_result(
                result
            )

            fingerprints = set()

            for image in result["images"]:

                fingerprint = prompt_fingerprint(
                    image["full_prompt"]
                )

                if fingerprint in fingerprints:

                    raise ValueError(
                        "Duplicate prompt detected."
                    )

                fingerprints.add(
                    fingerprint
                )

                score = score_prompt(
                    image["full_prompt"]
                )

                image["quality_score"] = score

                image["full_prompt"] = build_image_prompt(
                    image
                )

            print(
                "Gemini returned valid structured content."
            )

            return result

        except Exception as error:

            last_error = error

            print(
                f"Gemini attempt {attempt} failed:"
            )

            print(error)

            if attempt < 2:

                print(
                    "Retrying Gemini in 10 seconds..."
                )

                time.sleep(10)

    raise Exception(
        "Gemini failed after 2 attempts: "
        f"{last_error}"
    )


# ============================================================
# TELEGRAM API
# ============================================================

def telegram_request(
    method,
    data,
    content_type=(
        "application/x-www-form-urlencoded"
    ),
):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/{method}"
    )

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": content_type
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=120,
        ) as response:

            return json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

    except urllib.error.HTTPError as error:

        error_body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        print(
            f"Telegram HTTP error: {method}"
        )

        print(error_body)

        raise


# ============================================================
# SEND TELEGRAM TEXT
# ============================================================

def send_message(text):

    data = urllib.parse.urlencode(
        {
            "chat_id": CHANNEL,
            "text": text,
        }
    ).encode(
        "utf-8"
    )

    result = telegram_request(
        "sendMessage",
        data,
    )

    if not result.get("ok"):

        raise Exception(
            "Telegram sendMessage failed: "
            + str(result)
        )

    return result


# ============================================================
# SEND IMAGE ALBUM
# ============================================================

def send_media_group(
    image_files
):

    boundary = (
        "----TelegramBoundary987654321"
    )

    body = bytearray()

    def add_field(
        name,
        value,
    ):

        body.extend(
            f"--{boundary}\r\n".encode()
        )

        body.extend(
            (
                f'Content-Disposition: '
                f'form-data; name="{name}"'
                f'\r\n\r\n'
            ).encode()
        )

        body.extend(
            value.encode(
                "utf-8"
            )
        )

        body.extend(
            b"\r\n"
        )

    media = []

    for filename in image_files:

        media.append(
            {
                "type": "photo",
                "media": (
                    f"attach://{filename}"
                ),
            }
        )

    add_field(
        "chat_id",
        CHANNEL,
    )

    add_field(
        "media",
        json.dumps(media),
    )

    for filename in image_files:

        body.extend(
            f"--{boundary}\r\n".encode()
        )

        body.extend(
            (
                f'Content-Disposition: form-data; '
                f'name="{filename}"; '
                f'filename="{filename}"\r\n'
            ).encode()
        )

        body.extend(
            b"Content-Type: image/png\r\n\r\n"
        )

        with open(
            filename,
            "rb",
        ) as file:

            body.extend(
                file.read()
            )

        body.extend(
            b"\r\n"
        )

    body.extend(
        f"--{boundary}--\r\n".encode()
    )

    return telegram_request(
        "sendMediaGroup",
        bytes(body),
        content_type=(
            "multipart/form-data; "
            f"boundary={boundary}"
        ),
    )


# ============================================================
# BUILD TELEGRAM PROMPT LIBRARY
# ============================================================

def build_telegram_message(
    result
):

    title = result[
        "collection_title"
    ]

    description = result.get(
        "collection_description",
        "",
    )

    images = result[
        "images"
    ]

    message_parts = []

    message_parts.append(
        f"🎨 {title}"
    )

    message_parts.append(
        f"📚 {category['name']}"
    )

    message_parts.append(
        f"🗓 Theme: {weekly_theme}"
    )

    message_parts.append(
        f"\n{description}"
    )

    message_parts.append(
        "\n━━━━━━━━━━━━━━━━━━"
    )

    for index, image in enumerate(
        images,
        start=1,
    ):

        message_parts.append(
            f"\n🖼️ IMAGE {index} — "
            f"{image['concept_title']}"
        )

        message_parts.append(
            f"🎯 Difficulty: "
            f"{image['difficulty']}"
        )

        message_parts.append(
            f"📐 Ratio: "
            f"{image['aspect_ratio']}"
        )

        message_parts.append(
            f"⭐ Prompt quality: "
            f"{image['quality_score']}/14"
        )

        message_parts.append(
            "\n📋 COPY-READY PROMPT\n"
            + image["full_prompt"]
        )

        message_parts.append(
            "\n💡 WHY IT WORKS"
        )

        for point in image[
            "breakdown"
        ]:

            message_parts.append(
                f"• {point}"
            )

        message_parts.append(
            "\n━━━━━━━━━━━━━━━━━━"
        )

    message_parts.append(
        "\n🔥 Save this collection "
        "for later."
    )

    message_parts.append(
        "💬 Follow for useful AI image prompts."
    )

    return "\n".join(
        message_parts
    )


# ============================================================
# SAFE TELEGRAM MESSAGE CHUNKS
# ============================================================

def send_long_message(
    text
):

    max_length = 3900

    chunks = []

    while len(text) > max_length:

        split_position = text.rfind(
            "\n",
            0,
            max_length,
        )

        if split_position <= 0:

            split_position = max_length

        chunks.append(
            text[:split_position]
        )

        text = text[
            split_position:
        ].lstrip()

    if text:

        chunks.append(
            text
        )

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        print(
            f"Sending Telegram text "
            f"chunk {index}/{len(chunks)}..."
        )

        send_message(
            chunk
        )


# ============================================================
# CLEANUP
# ============================================================

def cleanup_files(
    image_files
):

    for filename in image_files:

        try:

            if os.path.exists(
                filename
            ):

                os.remove(
                    filename
                )

        except Exception as error:

            print(
                f"Cleanup failed for "
                f"{filename}: {error}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("")
    print(
        "======================================"
    )
    print(
        "AI TELEGRAM PROMPT LIBRARY MAX V2"
    )
    print(
        "======================================"
    )
    print("")

    print(
        "Today's category:",
        category["name"],
    )

    print(
        "Weekly theme:",
        weekly_theme,
    )

    print("")

    print(
        "Generating structured prompt collection..."
    )

    result = gemini_generate_content()

    print("")

    print(
        "Collection:",
        result["collection_title"],
    )

    print(
        "4 structured prompts generated."
    )

    image_files = []

    try:

        # ----------------------------------------------------
        # GENERATE IMAGES
        # ----------------------------------------------------

        for index, image in enumerate(
            result["images"],
            start=1,
        ):

            filename = (
                f"image_{index}.png"
            )

            print("")

            print(
                f"Generating image "
                f"{index}/4..."
            )

            print(
                f"Aspect ratio: "
                f"{image['aspect_ratio']}"
            )

            print(
                f"Quality score: "
                f"{image['quality_score']}/14"
            )

            download_image(
                image["full_prompt"],
                filename,
                image["aspect_ratio"],
            )

            image_files.append(
                filename
            )

        # ----------------------------------------------------
        # POST IMAGE ALBUM
        # ----------------------------------------------------

        print("")

        print(
            "Uploading 4 images to Telegram..."
        )

        telegram_result = send_media_group(
            image_files
        )

        if not telegram_result.get(
            "ok"
        ):

            raise Exception(
                "Telegram album failed: "
                + str(telegram_result)
            )

        print(
            "4 images posted successfully."
        )

        # ----------------------------------------------------
        # POST PROMPT LIBRARY
        # ----------------------------------------------------

        print("")

        print(
            "Building Telegram prompt library post..."
        )

        telegram_message = (
            build_telegram_message(
                result
            )
        )

        print(
            "Telegram message length:",
            len(telegram_message),
        )

        send_long_message(
            telegram_message
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        print("")

        print(
            "======================================"
        )

        print(
            "MAX V2 SUCCESS"
        )

        print(
            "======================================"
        )

        print(
            "Category:",
            category["name"],
        )

        print(
            "Theme:",
            weekly_theme,
        )

        print(
            "Collection:",
            result[
                "collection_title"
            ],
        )

        print(
            "Images:",
            len(
                result["images"]
            ),
        )

        print(
            "Smart aspect ratios: YES"
        )

        print(
            "Prompt scoring: YES"
        )

        print(
            "Dynamic negative prompts: YES"
        )

        print(
            "Image validation: YES"
        )

        print(
            "Automatic retries: YES"
        )

        print(
            "Duplicate detection: YES"
        )

        print(
            "Educational breakdowns: YES"
        )

        print("")

    finally:

        cleanup_files(
            image_files
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
