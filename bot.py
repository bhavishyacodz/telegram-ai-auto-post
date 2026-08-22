import datetime
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

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
# CONTROLLED CONTENT CATEGORIES
# ============================================================

CATEGORIES = [
    {
        "id": "cinematic_photography",
        "name": "Cinematic Photography",
        "description": "Realistic cinematic photography, portraits, streets, environments and dramatic scenes."
    },
    {
        "id": "game_art",
        "name": "Game Art",
        "description": "Game development concepts, characters, environments, worlds and cinematic game scenes."
    },
    {
        "id": "cyberpunk",
        "name": "Cyberpunk",
        "description": "Futuristic cities, technology, programmers, neon environments and cyberpunk storytelling."
    },
    {
        "id": "sci_fi",
        "name": "Science Fiction",
        "description": "Advanced technology, spacecraft, laboratories, futuristic worlds and speculative environments."
    },
    {
        "id": "fantasy",
        "name": "Fantasy",
        "description": "Epic fantasy environments, characters, magical worlds and cinematic storytelling."
    },
    {
        "id": "product_visuals",
        "name": "Product Visuals",
        "description": "Premium product photography, advertising concepts, commercial visuals and studio scenes."
    },
    {
        "id": "architecture",
        "name": "Architecture",
        "description": "Modern architecture, futuristic buildings, interiors, urban spaces and architectural photography."
    },
    {
        "id": "surreal_art",
        "name": "Surreal Art",
        "description": "Dreamlike, imaginative, unusual and visually striking conceptual scenes."
    }
]


# ============================================================
# DAILY CATEGORY SELECTION
# ============================================================

IST = datetime.timezone(
    datetime.timedelta(hours=5, minutes=30)
)

now = datetime.datetime.now(IST)

slot = 0 if now.hour < 15 else 1

day_number = now.timetuple().tm_yday

category_index = (
    ((day_number - 1) * 2) + slot
) % len(CATEGORIES)

category = CATEGORIES[category_index]


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
# GEMINI REQUEST
# ============================================================

PROMPT_REQUEST = f"""
You are the content engine for a professional AI image prompt library.

The goal is NOT to create random pretty images.

The goal is to create useful, original, copy-ready AI image prompts
that teach people how to create strong images.

Today's category:

{category["name"]}

Category description:

{category["description"]}

Permanent visual identity:

{STYLE}


Create EXACTLY 4 different image concepts for today's collection.

The four concepts must clearly belong to the same collection,
but they must be substantially different from one another.

Change the following between the four concepts:

- subject
- environment
- composition
- action
- camera perspective
- visual storytelling


IMPORTANT:

Do not make four variations of the same scene.

Each prompt must be independently useful.

Each prompt must be detailed enough to paste directly into
an image generation model.


For EACH image return these fields:

1. "concept_title"
   Short and memorable title.

2. "subject"
   The primary subject of the image.

3. "style"
   The visual style.

4. "composition"
   How the scene is arranged and framed.

5. "lighting"
   Lighting direction, quality and behavior.

6. "camera"
   Camera angle, distance, lens and depth of field.

7. "modifiers"
   Important visual modifiers such as atmosphere,
   texture, film grain, volumetric effects or realism.

8. "aspect_ratio"
   Choose the most appropriate ratio from ONLY:
   "1:1"
   "4:5"
   "16:9"
   "9:16"

Use:
- 4:5 for portrait/editorial/social imagery
- 9:16 for vertical cinematic scenes
- 16:9 for cinematic landscapes, environments and wide scenes
- 1:1 for square compositions or balanced artwork

9. "full_prompt"
   Combine the important information into ONE polished,
   detailed, copy-ready image-generation prompt.

10. "breakdown"
    Return EXACTLY 3 short explanations.

    Each explanation must teach why a particular prompt element
    improves the image.

    Example:
    "85mm lens → creates natural portrait compression."
    "Rim lighting → separates the subject from the dark background."
    "Shallow depth of field → keeps attention on the subject."


The full_prompt MUST include:

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


The full_prompt must NOT contain explanations outside the actual prompt.

Make the prompts original.

Do not copy known prompts from websites.

Do not mention OpenArt, PromptCreek, Reddit, Midjourney, Flux,
Stable Diffusion or any other external source.

Do not claim that a prompt was tested on any particular model.

Return ONLY valid JSON.

EXACT JSON STRUCTURE:

{{
  "collection_title": "short collection title",
  "category": "{category["name"]}",
  "collection_description": "2 short sentences describing what this collection teaches or explores",
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
            "x-goog-api-key": GEMINI_KEY
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=120
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
                indent=2
            )[:5000]
        )

        raise Exception(
            "Gemini response did not contain valid text."
        ) from error


def validate_result(result):

    if not isinstance(result, dict):
        raise ValueError("Gemini result is not an object.")

    collection_title = result.get("collection_title")

    images = result.get("images")

    if not collection_title:
        raise ValueError(
            "Missing collection_title."
        )

    if not isinstance(images, list):
        raise ValueError(
            "Missing images list."
        )

    if len(images) != 4:
        raise ValueError(
            f"Expected exactly 4 images, got {len(images)}."
        )

    valid_ratios = {
        "1:1",
        "4:5",
        "16:9",
        "9:16"
    }

    for index, image in enumerate(images, start=1):

        if not isinstance(image, dict):
            raise ValueError(
                f"Image {index} is not an object."
            )

        required_fields = [
            "concept_title",
            "subject",
            "style",
            "composition",
            "lighting",
            "camera",
            "modifiers",
            "aspect_ratio",
            "full_prompt",
            "breakdown"
        ]

        for field in required_fields:

            if not image.get(field):
                raise ValueError(
                    f"Image {index} is missing '{field}'."
                )

        if image["aspect_ratio"] not in valid_ratios:
            raise ValueError(
                f"Image {index} has invalid aspect ratio."
            )

        if not isinstance(
            image["breakdown"],
            list
        ):
            raise ValueError(
                f"Image {index} breakdown is not a list."
            )

        if len(image["breakdown"]) != 3:
            raise ValueError(
                f"Image {index} must have exactly 3 breakdown points."
            )

    return result


def gemini_generate_content():

    last_error = None

    for attempt in range(1, 3):

        print(
            f"Gemini generation attempt {attempt}/2..."
        )

        try:

            raw_result = gemini_request()

            text = extract_gemini_text(
                raw_result
            )

            result = json.loads(text)

            result = validate_result(
                result
            )

            print(
                "Gemini returned valid structured content."
            )

            return result

        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            json.JSONDecodeError,
            ValueError,
            Exception
        ) as error:

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
        "Gemini failed to produce valid structured content "
        f"after 2 attempts: {last_error}"
    )


# ============================================================
# HUGGING FACE IMAGE GENERATION
# ============================================================

# ================================================================
# POLLINATIONS IMAGE GENERATION
# ================================================================

# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

def download_image(prompt, filename):
    print(
        f"Generating image with Pollinations: {filename}"
    )

    try:
        encoded_prompt = urllib.parse.quote(prompt)

        url = (
            "https://image.pollinations.ai/prompt/"
            f"{encoded_prompt}"
            "?width=1024"
            "&height=1024"
            "&nologo=true"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:
            image_data = response.read()

        with open(filename, "wb") as file:
            file.write(image_data)

        print(
            f"Saved image: {filename}"
        )

        return filename

    except Exception as error:
        print(
            f"Image generation failed: {error}"
        )
        raise


# ============================================================
# TELEGRAM API
# ============================================================

def telegram_request(
    method,
    data,
    content_type="application/x-www-form-urlencoded"
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
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:

        error_body = error.read().decode(
            "utf-8",
            errors="replace"
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
            "text": text
        }
    ).encode("utf-8")

    result = telegram_request(
        "sendMessage",
        data
    )

    if not result.get("ok"):

        raise Exception(
            "Telegram sendMessage failed: "
            + str(result)
        )

    return result


# ============================================================
# SEND 4 IMAGES AS TELEGRAM ALBUM
# ============================================================

def send_media_group(image_files):

    boundary = (
        "----TelegramBoundary987654321"
    )

    body = bytearray()


    def add_field(name, value):

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
            value.encode("utf-8")
        )

        body.extend(
            b"\r\n"
        )


    media = []

    for filename in image_files:

        media.append(
            {
                "type": "photo",
                "media": f"attach://{filename}"
            }
        )


    add_field(
        "chat_id",
        CHANNEL
    )

    add_field(
        "media",
        json.dumps(media)
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
            "rb"
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
        )
    )


# ============================================================
# BUILD TELEGRAM CONTENT
# ============================================================

def build_telegram_message(result):

    title = result["collection_title"]

    category_name = result.get(
        "category",
        category["name"]
    )

    description = result.get(
        "collection_description",
        ""
    )

    images = result["images"]

    message_parts = []

    message_parts.append(
        f"🎨 {title}"
    )

    message_parts.append(
        f"📚 Category: {category_name}"
    )

    if description:
        message_parts.append(
            f"\n{description}"
        )

    message_parts.append(
        "\n━━━━━━━━━━━━━━━━━━"
    )

    for index, image in enumerate(
        images,
        start=1
    ):

        message_parts.append(
            f"\n🖼️ IMAGE {index} — {image['concept_title']}"
        )

        message_parts.append(
            f"📐 Aspect ratio: {image['aspect_ratio']}"
        )

        message_parts.append(
            "\n📋 COPY-READY PROMPT\n"
            + image["full_prompt"]
        )

        message_parts.append(
            "\n💡 WHY IT WORKS"
        )

        for point in image["breakdown"]:

            message_parts.append(
                f"• {point}"
            )

        message_parts.append(
            "\n━━━━━━━━━━━━━━━━━━"
        )

    return "\n".join(
        message_parts
    )


# ============================================================
# SEND LONG TELEGRAM MESSAGE IN SAFE CHUNKS
# ============================================================

def send_long_message(text):

    max_length = 3900

    chunks = [
        text[i:i + max_length]
        for i in range(
            0,
            len(text),
            max_length
        )
    ]

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"Sending Telegram text chunk "
            f"{index}/{len(chunks)}..."
        )

        send_message(chunk)


# ============================================================
# MAIN
# ============================================================

def main():

    print("")
    print("======================================")
    print("AI TELEGRAM PROMPT LIBRARY V1")
    print("======================================")
    print("")

    print(
        "Today's category:",
        category["name"]
    )

    print(
        "Category description:",
        category["description"]
    )

    print("")
    print(
        "Generating structured prompt collection..."
    )

    result = gemini_generate_content()

    print("")
    print(
        "Collection:",
        result["collection_title"]
    )

    print(
        "4 structured prompts generated."
    )


    # --------------------------------------------------------
    # GENERATE IMAGES
    # ------------------------------------------


    image_files = []

    for index, image in enumerate(
        result["images"],
        start=1
    ):

        filename = (
            f"image_{index}.png"
        )

        print("")
        print(
            f"Generating image {index}/4..."
        )

        download_image(
            image["full_prompt"],
            filename
        )

        image_files.append(
            filename
        )


    # --------------------------------------------------------
    # POST IMAGE ALBUM
    # --------------------------------------------------------

    print("")
    print(
        "Uploading 4 images to Telegram..."
    )

    telegram_result = send_media_group(
        image_files
    )

    if not telegram_result.get("ok"):

        raise Exception(
            "Telegram album failed: "
            + str(telegram_result)
        )

    print(
        "4 images posted successfully."
    )


    # --------------------------------------------------------
    # POST PROMPT LIBRARY CONTENT
    # --------------------------------------------------------

    print("")
    print(
        "Building Telegram prompt library post..."
    )

    telegram_message = build_telegram_message(
        result
    )

    print(
        f"Telegram message length: "
        f"{len(telegram_message)} characters"
    )

    send_long_message(
        telegram_message
    )


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    print("")
    print("======================================")
    print("V1 SUCCESS")
    print("======================================")
    print("")
    print(
        "Category:",
        category["name"]
    )
    print(
        "Collection:",
        result["collection_title"]
    )
    print(
        "Images:",
        len(result["images"])
    )
    print(
        "Structured prompts: YES"
    )
    print(
        "Prompt breakdowns: YES"
    )
    print(
        "Aspect ratios: YES"
    )
    print("")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()


    
