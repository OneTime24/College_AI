import cv2
import random
import time
import math
import numpy as np


WINDOW_NAME = "AI College - Funny Face AR"
CAMERA_INDEX = 0
FILTER_CHANGE_TIME = 4


FACE_CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


# ============================================================
# FILTERS
# ============================================================

def sunglasses(frame, x, y, w, h):
    eye_y = y + int(h * 0.40)

    left_eye = (x + int(w * 0.32), eye_y)
    right_eye = (x + int(w * 0.68), eye_y)

    radius = max(12, int(w * 0.14))

    cv2.circle(frame, left_eye, radius, (20, 20, 20), -1)
    cv2.circle(frame, right_eye, radius, (20, 20, 20), -1)

    cv2.line(
        frame,
        (left_eye[0] + radius, eye_y),
        (right_eye[0] - radius, eye_y),
        (20, 20, 20),
        max(4, radius // 3)
    )

    cv2.line(
        frame,
        (x + int(w * 0.05), eye_y),
        (left_eye[0] - radius, eye_y),
        (20, 20, 20),
        max(3, radius // 3)
    )

    cv2.line(
        frame,
        (right_eye[0] + radius, eye_y),
        (x + int(w * 0.95), eye_y),
        (20, 20, 20),
        max(3, radius // 3)
    )


def moustache(frame, x, y, w, h):
    center_x = x + w // 2
    center_y = y + int(h * 0.64)

    size = max(10, int(w * 0.12))

    left_points = []
    right_points = []

    for i in range(21):
        t = i / 20

        left_x = int(center_x - size - t * size * 2)
        left_y = int(
            center_y + math.sin(t * math.pi) * size * 0.7
        )

        right_x = int(center_x + size + t * size * 2)
        right_y = int(
            center_y + math.sin(t * math.pi) * size * 0.7
        )

        left_points.append((left_x, left_y))
        right_points.append((right_x, right_y))

    cv2.polylines(
        frame,
        [np.array(left_points)],
        False,
        (30, 30, 30),
        max(4, size // 2)
    )

    cv2.polylines(
        frame,
        [np.array(right_points)],
        False,
        (30, 30, 30),
        max(4, size // 2)
    )


def clown(frame, x, y, w, h):
    center_x = x + w // 2

    nose_y = y + int(h * 0.62)
    nose_radius = max(10, int(w * 0.08))

    cv2.circle(
        frame,
        (center_x, nose_y),
        nose_radius,
        (0, 0, 255),
        -1
    )

    eye_radius = max(5, int(w * 0.04))

    cv2.circle(
        frame,
        (x + int(w * 0.30), y + int(h * 0.45)),
        eye_radius,
        (0, 0, 255),
        -1
    )

    cv2.circle(
        frame,
        (x + int(w * 0.70), y + int(h * 0.45)),
        eye_radius,
        (0, 0, 255),
        -1
    )

    cv2.ellipse(
        frame,
        (center_x, y + int(h * 0.72)),
        (int(w * 0.22), int(h * 0.10)),
        0,
        0,
        180,
        (0, 0, 255),
        4
    )


def dog_ears(frame, x, y, w, h):
    ear_width = int(w * 0.35)
    ear_height = int(h * 0.30)

    left = np.array([
        [
            x + int(w * 0.10),
            y + int(h * 0.12)
        ],
        [
            x + int(w * 0.10) - ear_width // 2,
            y - ear_height
        ],
        [
            x + int(w * 0.32),
            y + int(h * 0.25)
        ]
    ])

    right = np.array([
        [
            x + int(w * 0.90),
            y + int(h * 0.12)
        ],
        [
            x + int(w * 0.90) + ear_width // 2,
            y - ear_height
        ],
        [
            x + int(w * 0.68),
            y + int(h * 0.25)
        ]
    ])

    cv2.fillConvexPoly(
        frame,
        left,
        (70, 55, 35)
    )

    cv2.fillConvexPoly(
        frame,
        right,
        (70, 55, 35)
    )

    cv2.polylines(
        frame,
        [left],
        True,
        (30, 30, 30),
        3
    )

    cv2.polylines(
        frame,
        [right],
        True,
        (30, 30, 30),
        3
    )


def crown(frame, x, y, w, h):
    crown_top = y - int(h * 0.25)

    points = np.array([
        [
            x + int(w * 0.12),
            y + int(h * 0.05)
        ],
        [
            x + int(w * 0.27),
            crown_top
        ],
        [
            x + int(w * 0.50),
            y + int(h * 0.04)
        ],
        [
            x + int(w * 0.73),
            crown_top
        ],
        [
            x + int(w * 0.88),
            y + int(h * 0.05)
        ],
        [
            x + int(w * 0.82),
            y + int(h * 0.20)
        ],
        [
            x + int(w * 0.18),
            y + int(h * 0.20)
        ]
    ], dtype=np.int32)

    cv2.fillPoly(
        frame,
        [points],
        (0, 215, 255)
    )

    cv2.polylines(
        frame,
        [points],
        True,
        (30, 150, 180),
        3
    )


def emoji(frame, x, y, w, h):
    center_x = x + w // 2
    center_y = y + int(h * 0.60)

    radius = max(20, int(w * 0.30))

    cv2.circle(
        frame,
        (center_x, center_y),
        radius,
        (0, 220, 255),
        -1
    )

    eye_radius = max(3, radius // 8)

    cv2.circle(
        frame,
        (
            center_x - radius // 3,
            center_y - radius // 4
        ),
        eye_radius,
        (0, 0, 0),
        -1
    )

    cv2.circle(
        frame,
        (
            center_x + radius // 3,
            center_y - radius // 4
        ),
        eye_radius,
        (0, 0, 0),
        -1
    )

    cv2.ellipse(
        frame,
        (
            center_x,
            center_y + radius // 6
        ),
        (
            radius // 2,
            radius // 3
        ),
        0,
        10,
        170,
        (0, 0, 0),
        3
    )


FILTERS = {
    "Sunglasses": sunglasses,
    "Moustache": moustache,
    "Clown": clown,
    "Dog Ears": dog_ears,
    "Crown": crown,
    "Emoji": emoji
}


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 50)
    print("       AI COLLEGE - FUNNY FACE AR")
    print("=" * 50)

    print("\nAvailable filters:")

    filter_names = list(FILTERS.keys())

    for index, name in enumerate(filter_names, 1):
        print(f"{index}. {name}")

    print("\nControls:")
    print("R     = Random filter")
    print("1-6   = Select filter")
    print("Q     = Quit")
    print("ESC   = Quit")

    # --------------------------------------------------------
    # Face detector
    # --------------------------------------------------------

    detector = cv2.CascadeClassifier(FACE_CASCADE)

    if detector.empty():
        print("\nERROR: Could not load face detector.")
        return

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("\nERROR: Could not open camera.")
        print("Try changing CAMERA_INDEX from 0 to 1.")
        return

    # Camera resolution

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    # --------------------------------------------------------
    # Initial filter
    # --------------------------------------------------------

    current_filter = random.choice(filter_names)

    last_filter_change = time.time()

    print("\nCamera started.")
    print(f"Current filter: {current_filter}")
    print("\nPress Q to exit.\n")

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    while True:

        success, frame = camera.read()

        if not success:
            print("ERROR: Failed to read camera frame.")
            break

        # Mirror the camera like a normal selfie camera

        frame = cv2.flip(frame, 1)

        # ----------------------------------------------------
        # Convert to grayscale
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # ----------------------------------------------------
        # Detect faces
        # ----------------------------------------------------

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(80, 80)
        )

        # ----------------------------------------------------
        # Automatically change filter
        # ----------------------------------------------------

        if (
            time.time() - last_filter_change
            >= FILTER_CHANGE_TIME
        ):

            current_filter = random.choice(
                filter_names
            )

            last_filter_change = time.time()

        # ----------------------------------------------------
        # Apply filter to every detected face
        # ----------------------------------------------------

        filter_function = FILTERS[current_filter]

        for (
            x,
            y,
            width,
            height
        ) in faces:

            filter_function(
                frame,
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # HUD
        # ----------------------------------------------------

        height, width = frame.shape[:2]

        # Header

        cv2.rectangle(
            frame,
            (0, 0),
            (width, 85),
            (20, 20, 20),
            -1
        )

        # Title

        cv2.putText(
            frame,
            "AI COLLEGE",
            (25, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2
        )

        # Subtitle

        cv2.putText(
            frame,
            "OFFLINE FUNNY FACE",
            (25, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1
        )

        # Current filter

        cv2.putText(
            frame,
            f"FILTER: {current_filter}",
            (width - 300, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )

        # Face count

        cv2.putText(
            frame,
            f"FACES: {len(faces)}",
            (width - 300, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1
        )

        # ----------------------------------------------------
        # Bottom controls
        # ----------------------------------------------------

        cv2.rectangle(
            frame,
            (0, height - 45),
            (width, height),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            frame,
            "R: Random    1-6: Filter    Q: Exit",
            (20, height - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (220, 220, 220),
            1
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        cv2.imshow(
            WINDOW_NAME,
            frame
        )

        # ----------------------------------------------------
        # Keyboard
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        # Quit

        if key in (
            ord("q"),
            ord("Q"),
            27
        ):
            break

        # Random filter

        elif key in (
            ord("r"),
            ord("R")
        ):

            current_filter = random.choice(
                filter_names
            )

            last_filter_change = time.time()

        # Number keys

        elif ord("1") <= key <= ord("6"):

            index = key - ord("1")

            if index < len(filter_names):

                current_filter = filter_names[index]

                last_filter_change = time.time()

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    print("\nFunny Face AR stopped.")


if __name__ == "__main__":
    main()