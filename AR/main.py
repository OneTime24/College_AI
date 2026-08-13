import cv2
import random
import time
import math
import numpy as np


WINDOW_NAME = "AI COLLEGE | OFFLINE AR"

CAMERA_INDEX = 0

MIN_FACE_WIDTH = 170
RESET_DELAY = 1.2

FACE_CASCADE = cv2.data.haarcascades + \
    "haarcascade_frontalface_default.xml"


# ============================================================
# DRAWING HELPERS
# ============================================================

def ellipse(frame, center, axes, color, thickness=-1):
    cv2.ellipse(
        frame,
        center,
        axes,
        0,
        0,
        360,
        color,
        thickness
    )


def polygon(frame, points, color):
    pts = np.array(points, dtype=np.int32)
    cv2.fillPoly(frame, [pts], color)


def text_center(frame, text, y, scale=0.7, thickness=2):
    size = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        thickness
    )[0]

    x = (frame.shape[1] - size[0]) // 2

    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA
    )


# ============================================================
# SUNGLASSES
# ============================================================

def filter_sunglasses(frame, x, y, w, h):

    ey = y + int(h * 0.40)

    left = (
        x + int(w * 0.32),
        ey
    )

    right = (
        x + int(w * 0.68),
        ey
    )

    r = max(15, int(w * 0.14))

    cv2.ellipse(
        frame,
        left,
        (r, int(r * 0.65)),
        0,
        0,
        360,
        (10, 10, 10),
        -1
    )

    cv2.ellipse(
        frame,
        right,
        (r, int(r * 0.65)),
        0,
        0,
        360,
        (10, 10, 10),
        -1
    )

    cv2.line(
        frame,
        (left[0] + r, ey),
        (right[0] - r, ey),
        (10, 10, 10),
        max(5, int(w * 0.025))
    )

    cv2.line(
        frame,
        (x, ey - 3),
        (left[0] - r, ey),
        (10, 10, 10),
        5
    )

    cv2.line(
        frame,
        (right[0] + r, ey),
        (x + w, ey - 3),
        (10, 10, 10),
        5
    )

def filter_moustache(frame, x, y, w, h):

    cx = x + w // 2
    cy = y + int(h * 0.64)

    size = max(12, int(w * 0.10))

    for side in (-1, 1):

        points = []

        for i in range(20):

            t = i / 19

            px = int(
                cx
                + side * (
                    size
                    + t * size * 2
                )
            )

            py = int(
                cy
                + math.sin(t * math.pi)
                * size * .65
            )

            points.append(
                (px, py)
            )

        cv2.polylines(
            frame,
            [np.array(points)],
            False,
            (25, 25, 25),
            max(5, size // 2)
        )

# ============================================================
# BIG EYES
# ============================================================

def filter_big_eyes(frame, x, y, w, h):

    ey = y + int(h * 0.40)

    r = max(
        18,
        int(w * 0.13)
    )

    left = (
        x + int(w * 0.32),
        ey
    )

    right = (
        x + int(w * 0.68),
        ey
    )

    # White eyes

    cv2.circle(
        frame,
        left,
        r,
        (245, 245, 245),
        -1
    )

    cv2.circle(
        frame,
        right,
        r,
        (245, 245, 245),
        -1
    )

    # Pupils

    pupil = max(5, r // 3)

    cv2.circle(
        frame,
        left,
        pupil,
        (20, 20, 20),
        -1
    )

    cv2.circle(
        frame,
        right,
        pupil,
        (20, 20, 20),
        -1
    )

    # Highlights

    cv2.circle(
        frame,
        (
            left[0] - pupil // 3,
            left[1] - pupil // 3
        ),
        max(2, pupil // 3),
        (255, 255, 255),
        -1
    )

    cv2.circle(
        frame,
        (
            right[0] - pupil // 3,
            right[1] - pupil // 3
        ),
        max(2, pupil // 3),
        (255, 255, 255),
        -1
    )


# ============================================================
# ALIEN
# ============================================================

def filter_alien(frame, x, y, w, h):

    ey = y + int(h * 0.40)

    r = max(
        20,
        int(w * 0.15)
    )

    left = (
        x + int(w * 0.30),
        ey
    )

    right = (
        x + int(w * 0.70),
        ey
    )

    cv2.ellipse(
        frame,
        left,
        (r, int(r * 1.35)),
        -10,
        0,
        360,
        (20, 230, 20),
        -1
    )

    cv2.ellipse(
        frame,
        right,
        (r, int(r * 1.35)),
        10,
        0,
        360,
        (20, 230, 20),
        -1
    )

    cv2.ellipse(
        frame,
        left,
        (int(r * .45), int(r * .85)),
        0,
        0,
        360,
        (5, 5, 5),
        -1
    )

    cv2.ellipse(
        frame,
        right,
        (int(r * .45), int(r * .85)),
        0,
        0,
        360,
        (5, 5, 5),
        -1
    )

    # Alien antenna

    cx = x + w // 2

    cv2.line(
        frame,
        (cx, y),
        (cx, y - int(h * .22)),
        (20, 230, 20),
        4
    )

    cv2.circle(
        frame,
        (cx, y - int(h * .22)),
        8,
        (0, 255, 255),
        -1
    )


# ============================================================
# DOG
# ============================================================

def filter_dog(frame, x, y, w, h):

    # Ears

    left = [
        (x + int(w * .18), y + int(h * .18)),
        (x - int(w * .02), y - int(h * .22)),
        (x + int(w * .38), y + int(h * .20))
    ]

    right = [
        (x + int(w * .82), y + int(h * .18)),
        (x + int(w * 1.02), y - int(h * .22)),
        (x + int(w * .62), y + int(h * .20))
    ]

    polygon(
        frame,
        left,
        (75, 45, 25)
    )

    polygon(
        frame,
        right,
        (75, 45, 25)
    )

    # Nose

    nose = (
        x + w // 2,
        y + int(h * .63)
    )

    cv2.ellipse(
        frame,
        nose,
        (
            int(w * .08),
            int(h * .055)
        ),
        0,
        0,
        360,
        (20, 20, 20),
        -1
    )

    # Tongue

    cv2.ellipse(
        frame,
        (
            x + w // 2,
            y + int(h * .76)
        ),
        (
            int(w * .08),
            int(h * .13)
        ),
        0,
        0,
        180,
        (100, 80, 220),
        -1
    )


# ============================================================
# CAT
# ============================================================

def filter_cat(frame, x, y, w, h):

    left = [
        (x + int(w * .12), y + int(h * .25)),
        (x + int(w * .10), y - int(h * .20)),
        (x + int(w * .42), y + int(h * .12))
    ]

    right = [
        (x + int(w * .88), y + int(h * .25)),
        (x + int(w * .90), y - int(h * .20)),
        (x + int(w * .58), y + int(h * .12))
    ]

    polygon(
        frame,
        left,
        (160, 100, 220)
    )

    polygon(
        frame,
        right,
        (160, 100, 220)
    )

    # Nose

    cv2.circle(
        frame,
        (
            x + w // 2,
            y + int(h * .64)
        ),
        max(7, int(w * .035)),
        (120, 80, 180),
        -1
    )

    # Whiskers

    cx = x + w // 2
    cy = y + int(h * .65)

    for direction in (-1, 1):

        for offset in (-1, 0, 1):

            cv2.line(
                frame,
                (cx, cy + offset * 7),
                (
                    cx + direction * int(w * .40),
                    cy + offset * 12
                ),
                (220, 220, 220),
                2
            )


# ============================================================
# DEVIL
# ============================================================

def filter_devil(frame, x, y, w, h):

    left = [
        (x + int(w * .15), y + int(h * .12)),
        (x + int(w * .05), y - int(h * .35)),
        (x + int(w * .40), y + int(h * .12))
    ]

    right = [
        (x + int(w * .85), y + int(h * .12)),
        (x + int(w * .95), y - int(h * .35)),
        (x + int(w * .60), y + int(h * .12))
    ]

    polygon(
        frame,
        left,
        (30, 30, 220)
    )

    polygon(
        frame,
        right,
        (30, 30, 220)
    )

    # Red eyes

    ey = y + int(h * .42)

    for ex in (
        x + int(w * .32),
        x + int(w * .68)
    ):

        cv2.ellipse(
            frame,
            (ex, ey),
            (
                int(w * .09),
                int(h * .045)
            ),
            0,
            0,
            360,
            (0, 0, 255),
            -1
        )


# ============================================================
# CLOWN
# ============================================================

def filter_clown(frame, x, y, w, h):

    cx = x + w // 2

    # Red nose

    cv2.circle(
        frame,
        (
            cx,
            y + int(h * .62)
        ),
        max(10, int(w * .08)),
        (0, 0, 255),
        -1
    )

    # Eye circles

    ey = y + int(h * .43)

    for ex in (
        x + int(w * .30),
        x + int(w * .70)
    ):

        cv2.circle(
            frame,
            (ex, ey),
            max(7, int(w * .05)),
            (255, 0, 255),
            -1
        )

    # Big smile

    cv2.ellipse(
        frame,
        (
            cx,
            y + int(h * .72)
        ),
        (
            int(w * .23),
            int(h * .13)
        ),
        0,
        0,
        180,
        (0, 0, 255),
        5
    )


# ============================================================
# COWBOY
# ============================================================

def filter_cowboy(frame, x, y, w, h):

    cx = x + w // 2

    # Hat

    cv2.ellipse(
        frame,
        (
            cx,
            y - int(h * .08)
        ),
        (
            int(w * .58),
            int(h * .14)
        ),
        0,
        0,
        360,
        (35, 70, 120),
        -1
    )

    polygon(
        frame,
        [
            (
                x + int(w * .25),
                y - int(h * .08)
            ),
            (
                x + int(w * .35),
                y - int(h * .38)
            ),
            (
                x + int(w * .65),
                y - int(h * .38)
            ),
            (
                x + int(w * .75),
                y - int(h * .08)
            )
        ],
        (35, 70, 120)
    )

    # Hat band

    cv2.line(
        frame,
        (
            x + int(w * .30),
            y - int(h * .13)
        ),
        (
            x + int(w * .70),
            y - int(h * .13)
        ),
        (20, 20, 40),
        7
    )


# ============================================================
# CROWN
# ============================================================

def filter_crown(frame, x, y, w, h):

    points = [
        (
            x + int(w * .12),
            y + int(h * .10)
        ),
        (
            x + int(w * .20),
            y - int(h * .35)
        ),
        (
            x + int(w * .42),
            y - int(h * .08)
        ),
        (
            x + int(w * .50),
            y - int(h * .42)
        ),
        (
            x + int(w * .58),
            y - int(h * .08)
        ),
        (
            x + int(w * .80),
            y - int(h * .35)
        ),
        (
            x + int(w * .88),
            y + int(h * .10)
        )
    ]

    polygon(
        frame,
        points,
        (0, 215, 255)
    )

    cv2.polylines(
        frame,
        [np.array(points)],
        True,
        (0, 160, 220),
        4
    )

    # Jewels

    for px in (
        x + int(w * .30),
        x + int(w * .50),
        x + int(w * .70)
    ):

        cv2.circle(
            frame,
            (
                px,
                y + int(h * .02)
            ),
            7,
            (0, 0, 255),
            -1
        )


# ============================================================
# NERD
# ============================================================

def filter_nerd(frame, x, y, w, h):

    ey = y + int(h * .42)

    r = int(w * .15)

    left = (
        x + int(w * .32),
        ey
    )

    right = (
        x + int(w * .68),
        ey
    )

    for eye in (left, right):

        cv2.rectangle(
            frame,
            (
                eye[0] - r,
                eye[1] - int(r * .7)
            ),
            (
                eye[0] + r,
                eye[1] + int(r * .7)
            ),
            (30, 30, 30),
            7
        )

    cv2.line(
        frame,
        (
            left[0] + r,
            ey
        ),
        (
            right[0] - r,
            ey
        ),
        (30, 30, 30),
        6
    )


# ============================================================
# MONOCLE
# ============================================================

def filter_monocle(frame, x, y, w, h):

    cx = x + int(w * .34)
    cy = y + int(h * .40)

    r = int(w * .16)

    cv2.circle(
        frame,
        (cx, cy),
        r,
        (190, 150, 50),
        6
    )

    cv2.line(
        frame,
        (
            cx + r,
            cy - r
        ),
        (
            cx + r + int(w * .10),
            cy - int(h * .18)
        ),
        (190, 150, 50),
        4
    )


# ============================================================
# ROBOT
# ============================================================

def filter_robot(frame, x, y, w, h):

    # Robot eyes

    ey = y + int(h * .42)

    for ex in (
        x + int(w * .32),
        x + int(w * .68)
    ):

        cv2.rectangle(
            frame,
            (
                ex - int(w * .08),
                ey - int(h * .06)
            ),
            (
                ex + int(w * .08),
                ey + int(h * .06)
            ),
            (180, 220, 255),
            -1
        )

    # Robot antenna

    cx = x + w // 2

    cv2.line(
        frame,
        (
            cx,
            y
        ),
        (
            cx,
            y - int(h * .25)
        ),
        (180, 180, 180),
        5
    )

    cv2.circle(
        frame,
        (
            cx,
            y - int(h * .25)
        ),
        10,
        (0, 0, 255),
        -1
    )

    # Robot mouth

    cv2.rectangle(
        frame,
        (
            x + int(w * .30),
            y + int(h * .70)
        ),
        (
            x + int(w * .70),
            y + int(h * .77)
        ),
        (180, 220, 255),
        -1
    )


# ============================================================
# BIG MOUTH
# ============================================================

def filter_big_mouth(frame, x, y, w, h):

    cx = x + w // 2
    cy = y + int(h * .70)

    cv2.ellipse(
        frame,
        (cx, cy),
        (
            int(w * .25),
            int(h * .15)
        ),
        0,
        0,
        360,
        (30, 30, 30),
        -1
    )

    # Teeth

    cv2.rectangle(
        frame,
        (
            cx - int(w * .18),
            cy - int(h * .08)
        ),
        (
            cx + int(w * .18),
            cy
        ),
        (245, 245, 245),
        -1
    )


# ============================================================
# FACE ACCESSORY COMBINATIONS
# ============================================================

def combo_random(frame, x, y, w, h):

    effects = [
        filter_sunglasses,
        filter_crown,
        filter_moustache,
        filter_big_eyes,
        filter_nerd,
        filter_monocle
    ]

    chosen = random.sample(
        effects,
        random.randint(2, 3)
    )

    for effect in chosen:

        effect(
            frame,
            x,
            y,
            w,
            h
        )


# ============================================================
# FILTER LIST
# ============================================================

FILTERS = [
    ("Sunglasses", filter_sunglasses),
    ("Big Eyes", filter_big_eyes),
    ("Alien", filter_alien),
    ("Dog", filter_dog),
    ("Cat", filter_cat),
    ("Devil", filter_devil),
    ("Clown", filter_clown),
    ("Cowboy", filter_cowboy),
    ("King", filter_crown),
    ("Nerd", filter_nerd),
    ("Monocle", filter_monocle),
    ("Robot", filter_robot),
    ("Big Mouth", filter_big_mouth),
    ("Random Combo", combo_random)
]


# ============================================================
# PARTICLES
# ============================================================

def draw_particles(frame, x, y, w, h):

    random.seed(
        int(time.time() * 2)
    )

    symbols = [
        "★",
        "♥",
        "✦"
    ]

    for _ in range(5):

        px = random.randint(
            x - int(w * .3),
            x + int(w * 1.3)
        )

        py = random.randint(
            y - int(h * .4),
            y + int(h * 1.2)
        )

        symbol = random.choice(
            symbols
        )

        cv2.putText(
            frame,
            symbol,
            (px, py),
            cv2.FONT_HERSHEY_SIMPLEX,
            random.uniform(.5, 1.0),
            (255, 220, 50),
            2,
            cv2.LINE_AA
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print("          AI COLLEGE - OFFLINE AR")
    print("=" * 55)
    print("Camera starting...")
    print("Waiting for visitors...")
    print()

    detector = cv2.CascadeClassifier(
        FACE_CASCADE
    )

    if detector.empty():

        print(
            "ERROR: Face detector failed."
        )

        return

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            "ERROR: Camera could not be opened."
        )

        return

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    active_filter = None
    filter_name = ""

    person_detected = False

    last_face_time = 0

    print("SYSTEM READY.")
    print()

    while True:

        success, frame = camera.read()

        if not success:
            continue

        frame = cv2.flip(
            frame,
            1
        )

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(100, 100)
        )

        closest_face = None

        if len(faces) > 0:

            closest_face = max(
                faces,
                key=lambda f: f[2] * f[3]
            )

        close_enough = False

        if closest_face is not None:

            x, y, w, h = closest_face

            if w >= MIN_FACE_WIDTH:

                close_enough = True

        # ====================================================
        # NEW VISITOR
        # ====================================================

        if close_enough:

            last_face_time = time.time()

            if not person_detected:

                person_detected = True

                filter_name, active_filter = random.choice(
                    FILTERS
                )

                print(
                    f"Visitor detected → {filter_name}"
                )

        # ====================================================
        # ACTIVE FILTER
        # ====================================================

        if person_detected and close_enough:

            x, y, w, h = closest_face

            active_filter(
                frame,
                x,
                y,
                w,
                h
            )

            draw_particles(
                frame,
                x,
                y,
                w,
                h
            )

        # ====================================================
        # PERSON LEFT
        # ====================================================

        if person_detected:

            if not close_enough:

                if (
                    time.time()
                    - last_face_time
                    > RESET_DELAY
                ):

                    person_detected = False

                    active_filter = None

                    filter_name = ""

                    print(
                        "Visitor left → waiting..."
                    )

        # ====================================================
        # UI
        # ====================================================

        height, width = frame.shape[:2]

        # Header

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (0, 0),
            (width, 82),
            (10, 10, 20),
            -1
        )

        frame = cv2.addWeighted(
            overlay,
            .88,
            frame,
            .12,
            0
        )

        cv2.putText(
            frame,
            "AI COLLEGE",
            (25, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            .85,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "OFFLINE AR EXPERIENCE",
            (25, 63),
            cv2.FONT_HERSHEY_SIMPLEX,
            .48,
            (170, 200, 255),
            1,
            cv2.LINE_AA
        )

        if person_detected:

            status = "AR FILTER ACTIVE"

            cv2.putText(
                frame,
                status,
                (
                    width - 270,
                    38
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                .55,
                (0, 255, 120),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                filter_name.upper(),
                (
                    width - 270,
                    65
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                .45,
                (255, 220, 100),
                1,
                cv2.LINE_AA
            )

        else:

            cv2.putText(
                frame,
                "READY",
                (
                    width - 130,
                    42
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                .55,
                (180, 180, 180),
                1,
                cv2.LINE_AA
            )

            text_center(
                frame,
                "STEP CLOSER",
                height // 2,
                .85,
                2
            )

        # Bottom bar

        cv2.rectangle(
            frame,
            (
                0,
                height - 38
            ),
            (
                width,
                height
            ),
            (10, 10, 20),
            -1
        )

        cv2.putText(
            frame,
            "100% OFFLINE  •  AI COLLEGE",
            (
                20,
                height - 13
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            .42,
            (150, 150, 150),
            1,
            cv2.LINE_AA
        )

        cv2.imshow(
            WINDOW_NAME,
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == 27:

            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()