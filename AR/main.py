import cv2
import mediapipe as mp
import numpy as np
import random
import time
import math

MODEL_PATH = "models/face_landmarker.task"

CAMERA_INDEX = 0
WIDTH = 640
HEIGHT = 480

MIN_FACE_WIDTH = 115
LOST_FACE_TIMEOUT = 1.0

WINDOW_NAME = "AI COLLEGE - OFFLINE AR"

mp_vision = mp.tasks.vision

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp_vision.FaceLandmarker
FaceLandmarkerOptions = mp_vision.FaceLandmarkerOptions
RunningMode = mp_vision.RunningMode


# ============================================================
# UTILITIES
# ============================================================

def p(landmarks, index, w, h):
    lm = landmarks[index]
    return np.array(
        [lm.x * w, lm.y * h],
        dtype=np.float32
    )


def dist(a, b):
    return float(np.linalg.norm(a - b))


def midpoint(a, b):
    return (a + b) / 2.0


def ellipse(frame, center, axes, color, thickness=-1):
    cv2.ellipse(
        frame,
        tuple(np.int32(center)),
        tuple(np.int32(axes)),
        0,
        0,
        360,
        color,
        thickness,
        cv2.LINE_AA
    )


def line(frame, a, b, color, thickness=2):
    cv2.line(
        frame,
        tuple(np.int32(a)),
        tuple(np.int32(b)),
        color,
        thickness,
        cv2.LINE_AA
    )


# ============================================================
# SMOOTHING
# ============================================================

class FaceSmoother:

    def __init__(self, alpha=0.45):
        self.alpha = alpha
        self.previous = None

    def update(self, points):

        if self.previous is None:
            self.previous = points.copy()
            return points

        self.previous = (
            self.previous * (1.0 - self.alpha)
            + points * self.alpha
        )

        return self.previous

    def reset(self):
        self.previous = None


# ============================================================
# FACE INFORMATION
# ============================================================

def get_face_info(landmarks, w, h):

    left = p(landmarks, 234, w, h)
    right = p(landmarks, 454, w, h)

    face_width = dist(left, right)

    left_eye_outer = p(landmarks, 33, w, h)
    left_eye_inner = p(landmarks, 133, w, h)

    right_eye_inner = p(landmarks, 362, w, h)
    right_eye_outer = p(landmarks, 263, w, h)

    left_eye = midpoint(
        left_eye_outer,
        left_eye_inner
    )

    right_eye = midpoint(
        right_eye_outer,
        right_eye_inner
    )

    nose = p(landmarks, 1, w, h)

    mouth_left = p(landmarks, 61, w, h)
    mouth_right = p(landmarks, 291, w, h)

    mouth = midpoint(
        mouth_left,
        mouth_right
    )

    chin = p(landmarks, 152, w, h)

    forehead = p(landmarks, 10, w, h)

    return {
        "width": face_width,
        "left_eye": left_eye,
        "right_eye": right_eye,
        "left_eye_width": dist(
            left_eye_outer,
            left_eye_inner
        ),
        "right_eye_width": dist(
            right_eye_outer,
            right_eye_inner
        ),
        "nose": nose,
        "mouth": mouth,
        "mouth_width": dist(
            mouth_left,
            mouth_right
        ),
        "chin": chin,
        "forehead": forehead,
        "left": left,
        "right": right,
    }


# ============================================================
# FACE DISTORTION
# ============================================================

def remap_face(
    frame,
    center,
    radius_x,
    radius_y,
    scale_x,
    scale_y
):

    h, w = frame.shape[:2]

    x0 = max(0, int(center[0] - radius_x))
    x1 = min(w, int(center[0] + radius_x))

    y0 = max(0, int(center[1] - radius_y))
    y1 = min(h, int(center[1] + radius_y))

    if x1 <= x0 or y1 <= y0:
        return frame

    roi = frame[y0:y1, x0:x1]

    rh, rw = roi.shape[:2]

    if rw < 5 or rh < 5:
        return frame

    yy, xx = np.mgrid[0:rh, 0:rw].astype(np.float32)

    cx = rw / 2.0
    cy = rh / 2.0

    nx = (xx - cx) / max(cx, 1)
    ny = (yy - cy) / max(cy, 1)

    sx = 1.0 / max(scale_x, 0.05)
    sy = 1.0 / max(scale_y, 0.05)

    map_x = cx + nx * cx * sx
    map_y = cy + ny * cy * sy

    map_x = np.clip(map_x, 0, rw - 1)
    map_y = np.clip(map_y, 0, rh - 1)

    warped = cv2.remap(
        roi,
        map_x,
        map_y,
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )

    mask = np.zeros(
        (rh, rw),
        dtype=np.uint8
    )

    cv2.ellipse(
        mask,
        (int(cx), int(cy)),
        (
            int(rw * 0.48),
            int(rh * 0.48)
        ),
        0,
        0,
        360,
        255,
        -1,
        cv2.LINE_AA
    )

    mask = cv2.GaussianBlur(
        mask,
        (21, 21),
        0
    )

    alpha = (
        mask.astype(np.float32)
        / 255.0
    )[:, :, None]

    result = (
        warped.astype(np.float32) * alpha
        + roi.astype(np.float32) * (1 - alpha)
    )

    frame[y0:y1, x0:x1] = result.astype(
        np.uint8
    )

    return frame


# ============================================================
# FILTER 1 - ALIEN
# ============================================================

def alien_filter(frame, f):

    width = f["width"]

    # Face deformation
    frame = remap_face(
        frame,
        midpoint(f["forehead"], f["chin"]),
        width * 0.72,
        width * 0.90,
        0.78,
        1.12
    )

    # Eyes
    for eye in (
        f["left_eye"],
        f["right_eye"]
    ):

        size = width * 0.17

        ellipse(
            frame,
            eye,
            (size, size * 1.25),
            (12, 8, 15)
        )

        ellipse(
            frame,
            eye,
            (size * .65, size * .90),
            (70, 220, 255)
        )

        ellipse(
            frame,
            eye,
            (size * .20, size * .75),
            (5, 5, 10)
        )

        ellipse(
            frame,
            eye - np.array(
                [size * .20, size * .25]
            ),
            (size * .10, size * .10),
            (255, 255, 255)
        )

    # Alien mouth
    ellipse(
        frame,
        f["mouth"],
        (
            f["mouth_width"] * .42,
            width * .025
        ),
        (20, 5, 25)
    )

    return frame


# ============================================================
# FILTER 2 - DOG
# ============================================================

def dog_filter(frame, f):

    width = f["width"]

    # Ears
    left = f["left"] + np.array(
        [-width * .15, -width * .40]
    )

    right = f["right"] + np.array(
        [width * .15, -width * .40]
    )

    for ear in (left, right):

        pts = np.array([
            ear + [-width * .18, -width * .05],
            ear + [width * .18, -width * .05],
            ear + [0, width * .35]
        ], dtype=np.int32)

        cv2.fillPoly(
            frame,
            [pts],
            (65, 45, 30)
        )

        inner = pts.astype(
            np.float32
        )

        inner[:, 1] += width * .04

        cv2.polylines(
            frame,
            [inner.astype(np.int32)],
            True,
            (110, 70, 50),
            4,
            cv2.LINE_AA
        )

    # Nose
    nose = f["nose"]

    ellipse(
        frame,
        nose + [0, width * .02],
        (
            width * .08,
            width * .055
        ),
        (20, 15, 15)
    )

    # Tongue
    tongue = f["mouth"] + [
        0,
        width * .12
    ]

    cv2.ellipse(
        frame,
        tuple(np.int32(tongue)),
        (
            int(width * .06),
            int(width * .14)
        ),
        0,
        0,
        360,
        (80, 90, 210),
        -1,
        cv2.LINE_AA
    )

    return frame


# ============================================================
# FILTER 3 - CLOWN
# ============================================================

def clown_filter(frame, f):

    width = f["width"]

    # Giant nose
    ellipse(
        frame,
        f["nose"],
        (
            width * .10,
            width * .10
        ),
        (30, 30, 220)
    )

    # Huge mouth
    mouth = f["mouth"]

    ellipse(
        frame,
        mouth + [0, width * .025],
        (
            f["mouth_width"] * .60,
            width * .16
        ),
        (25, 10, 20)
    )

    ellipse(
        frame,
        mouth + [0, width * .015],
        (
            f["mouth_width"] * .45,
            width * .075
        ),
        (245, 245, 245)
    )

    # Forehead decoration
    for i in range(5):

        angle = i * math.pi / 4

        x = (
            f["forehead"][0]
            + math.cos(angle) * width * .25
        )

        y = (
            f["forehead"][1]
            + math.sin(angle) * width * .25
        )

        cv2.circle(
            frame,
            (int(x), int(y)),
            int(width * .025),
            (40, 40, 220),
            -1,
            cv2.LINE_AA
        )

    return frame


# ============================================================
# FILTER 4 - ROBOT
# ============================================================

def robot_filter(frame, f):

    width = f["width"]

    # Dark face visor
    center = midpoint(
        f["forehead"],
        f["chin"]
    )

    overlay = frame.copy()

    cv2.ellipse(
        overlay,
        tuple(np.int32(center)),
        (
            int(width * .45),
            int(width * .55)
        ),
        0,
        0,
        360,
        (30, 35, 40),
        -1,
        cv2.LINE_AA
    )

    mask = np.zeros(
        frame.shape[:2],
        dtype=np.uint8
    )

    cv2.ellipse(
        mask,
        tuple(np.int32(center)),
        (
            int(width * .44),
            int(width * .53)
        ),
        0,
        0,
        360,
        255,
        -1
    )

    mask = cv2.GaussianBlur(
        mask,
        (31, 31),
        0
    )[:, :, None] / 255.0

    frame[:] = (
        overlay * mask
        + frame * (1 - mask)
    ).astype(np.uint8)

    for eye in (
        f["left_eye"],
        f["right_eye"]
    ):

        cv2.rectangle(
            frame,
            (
                int(eye[0] - width * .08),
                int(eye[1] - width * .025)
            ),
            (
                int(eye[0] + width * .08),
                int(eye[1] + width * .025)
            ),
            (80, 230, 255),
            -1
        )

    # Robot mouth
    x = int(f["mouth"][0])
    y = int(f["mouth"][1])

    cv2.line(
        frame,
        (x - int(width * .15), y),
        (x + int(width * .15), y),
        (80, 230, 255),
        4
    )

    return frame


# ============================================================
# FILTER 5 - GIANT FACE
# ============================================================

def giant_face_filter(frame, f):

    width = f["width"]

    # Enlarged entire face
    frame = remap_face(
        frame,
        midpoint(
            f["forehead"],
            f["chin"]
        ),
        width * .70,
        width * .85,
        1.25,
        1.18
    )

    # Giant eyes
    for eye in (
        f["left_eye"],
        f["right_eye"]
    ):

        size = width * .13

        ellipse(
            frame,
            eye,
            (
                size * 1.45,
                size * 1.15
            ),
            (245, 245, 245)
        )

        ellipse(
            frame,
            eye,
            (
                size * .50,
                size * .75
            ),
            (20, 20, 20)
        )

    return frame


# ============================================================
# FILTER 6 - OLD MAN
# ============================================================

def old_man_filter(frame, f):

    width = f["width"]

    # Gray hair
    hair_center = f["forehead"] + [
        0,
        -width * .12
    ]

    ellipse(
        frame,
        hair_center,
        (
            width * .38,
            width * .15
        ),
        (155, 155, 155)
    )

    # Eyebrows
    line(
        frame,
        f["left_eye"] + [-width * .10, -width * .06],
        f["left_eye"] + [width * .10, -width * .08],
        (90, 90, 90),
        5
    )

    line(
        frame,
        f["right_eye"] + [-width * .10, -width * .08],
        f["right_eye"] + [width * .10, -width * .06],
        (90, 90, 90),
        5
    )

    # Beard
    beard_center = f["chin"]

    ellipse(
        frame,
        beard_center + [0, -width * .03],
        (
            width * .25,
            width * .22
        ),
        (110, 110, 110)
    )

    # Wrinkles
    for offset in (-0.06, -0.025, 0.025, 0.06):

        y = f["forehead"][1] + width * offset

        line(
            frame,
            f["forehead"] + [-width * .16, y - f["forehead"][1]],
            f["forehead"] + [width * .16, y - f["forehead"][1]],
            (100, 100, 100),
            1
        )

    return frame


# ============================================================
# FILTER 7 - CROWN
# ============================================================

def crown_filter(frame, f):

    width = f["width"]

    base_y = int(
        f["forehead"][1] - width * .12
    )

    left_x = int(
        f["forehead"][0] - width * .35
    )

    right_x = int(
        f["forehead"][0] + width * .35
    )

    points = np.array([
        [left_x, base_y],
        [left_x + int(width * .08), base_y - int(width * .28)],
        [left_x + int(width * .20), base_y - int(width * .08)],
        [left_x + int(width * .35), base_y - int(width * .35)],
        [left_x + int(width * .48), base_y - int(width * .08)],
        [right_x, base_y]
    ], dtype=np.int32)

    cv2.fillPoly(
        frame,
        [points],
        (20, 180, 245)
    )

    cv2.polylines(
        frame,
        [points],
        True,
        (0, 220, 255),
        4,
        cv2.LINE_AA
    )

    # Gems
    for x, y in points[1:-1]:

        cv2.circle(
            frame,
            (x, y),
            max(3, int(width * .025)),
            (255, 255, 255),
            -1,
            cv2.LINE_AA
        )

    return frame


# ============================================================
# FILTER 8 - WIZARD
# ============================================================

def wizard_filter(frame, f):

    width = f["width"]

    # Hat
    top = f["forehead"] + [
        0,
        -width * .25
    ]

    pts = np.array([
        [
            int(top[0] - width * .35),
            int(top[1] + width * .25)
        ],
        [
            int(top[0] + width * .35),
            int(top[1] + width * .25)
        ],
        [
            int(top[0] + width * .05),
            int(top[1] - width * .42)
        ]
    ], dtype=np.int32)

    cv2.fillPoly(
        frame,
        [pts],
        (100, 45, 145)
    )

    cv2.polylines(
        frame,
        [pts],
        True,
        (200, 130, 255),
        3,
        cv2.LINE_AA
    )

    # Beard
    beard = f["chin"]

    ellipse(
        frame,
        beard + [0, -width * .03],
        (
            width * .25,
            width * .28
        ),
        (70, 55, 50)
    )

    # Magic particles
    for i in range(12):

        angle = (
            i * math.pi * 2 / 12
        )

        radius = width * (
            .40 + (i % 3) * .10
        )

        x = (
            f["mouth"][0]
            + math.cos(angle) * radius
        )

        y = (
            f["mouth"][1]
            + math.sin(angle) * radius
        )

        cv2.circle(
            frame,
            (int(x), int(y)),
            max(2, int(width * .012)),
            (180, 120, 255),
            -1,
            cv2.LINE_AA
        )

    return frame


# ============================================================
# FILTER LIST
# ============================================================

FILTERS = [
    ("ALIEN", alien_filter),
    ("DOG", dog_filter),
    ("CLOWN", clown_filter),
    ("ROBOT", robot_filter),
    ("GIANT FACE", giant_face_filter),
    ("OLD MAN", old_man_filter),
    ("ROYAL", crown_filter),
    ("WIZARD", wizard_filter),
]


# ============================================================
# UI
# ============================================================

def draw_ui(frame, filter_name, active):

    h, w = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (w, 65),
        (8, 8, 15),
        -1
    )

    frame[:] = cv2.addWeighted(
        overlay,
        .82,
        frame,
        .18,
        0
    )

    cv2.putText(
        frame,
        "AI COLLEGE",
        (18, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        .65,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "OFFLINE AR",
        (18, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        .35,
        (170, 220, 230),
        1,
        cv2.LINE_AA
    )

    if active:

        text = filter_name

        cv2.putText(
            frame,
            text,
            (
                w - 150,
                38
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            .45,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

    else:

        cv2.putText(
            frame,
            "STEP INTO THE AR ZONE",
            (
                w - 235,
                38
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            .38,
            (180, 220, 220),
            1,
            cv2.LINE_AA
        )

    cv2.rectangle(
        frame,
        (0, h - 24),
        (w, h),
        (8, 8, 15),
        -1
    )

    cv2.putText(
        frame,
        "100% OFFLINE  •  AI COLLEGE EXHIBITION",
        (12, h - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        .30,
        (170, 200, 205),
        1,
        cv2.LINE_AA
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("                 AI COLLEGE")
    print("              OFFLINE AR ENGINE")
    print("=" * 60)
    print()
    print("Camera:", CAMERA_INDEX)
    print("Resolution:", WIDTH, "x", HEIGHT)
    print("Filters:", len(FILTERS))
    print()
    print("Waiting for visitor...")
    print()

    options = FaceLandmarkerOptions(

        base_options=BaseOptions(
            model_asset_path=MODEL_PATH
        ),

        running_mode=RunningMode.VIDEO,

        num_faces=1,

        min_face_detection_confidence=.50,

        min_face_presence_confidence=.50,

        min_tracking_confidence=.50,

        output_face_blendshapes=False,

        output_facial_transformation_matrixes=False
    )

    detector = FaceLandmarker.create_from_options(
        options
    )

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print("ERROR: Could not open camera.")

        detector.close()

        return

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        HEIGHT
    )

    camera.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

    smoother = FaceSmoother(
        alpha=.55
    )

    active_filter = None
    filter_name = ""

    visitor_active = False

    last_face_time = 0

    timestamp = 0

    previous_time = time.time()

    fps = 0

    frame_counter = 0

    fps_time = time.time()

    while True:

        ok, frame = camera.read()

        if not ok:
            continue

        frame = cv2.flip(
            frame,
            1
        )

        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp += 33

        result = detector.detect_for_video(
            image,
            timestamp
        )

        active = False

        if result.face_landmarks:

            landmarks = result.face_landmarks[0]

            info = get_face_info(
                landmarks,
                w,
                h
            )

            # ------------------------------------------------
            # PERSON IS CLOSE ENOUGH
            # ------------------------------------------------

            if info["width"] >= MIN_FACE_WIDTH:

                active = True

                last_face_time = time.time()

                if not visitor_active:

                    visitor_active = True

                    smoother.reset()

                    # Choose ONE random filter
                    # for this visitor.
                    active_filter = random.choice(
                        FILTERS
                    )

                    filter_name = active_filter[0]

                    print(
                        f"Visitor detected -> {filter_name}"
                    )

                # Smooth landmarks
                raw_points = np.array(
                    [
                        [lm.x * w, lm.y * h]
                        for lm in landmarks
                    ],
                    dtype=np.float32
                )

                smooth_points = smoother.update(
                    raw_points
                )

                # Reconstruct relevant information
                # from smoothed points.
                info["left_eye"] = smooth_points[33:134].mean(axis=0)
                info["right_eye"] = smooth_points[263:363].mean(axis=0)

                info["nose"] = smooth_points[1]
                info["mouth"] = smooth_points[13]

                info["mouth_width"] = dist(
                    smooth_points[61],
                    smooth_points[291]
                )

                info["forehead"] = smooth_points[10]
                info["chin"] = smooth_points[152]

                info["left"] = smooth_points[234]
                info["right"] = smooth_points[454]

                # ------------------------------------------------
                # RUN FILTER
                # ------------------------------------------------

                output = active_filter[1](
                    frame,
                    info
                )

            else:

                output = frame

        else:

            output = frame

        # ----------------------------------------------------
        # PERSON LEFT
        # ----------------------------------------------------

        if (
            visitor_active
            and time.time() - last_face_time
            > LOST_FACE_TIMEOUT
        ):

            visitor_active = False

            active_filter = None

            filter_name = ""

            smoother.reset()

            print(
                "Visitor left. Waiting for next visitor..."
            )

        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        frame_counter += 1

        now = time.time()

        if now - fps_time >= 1.0:

            fps = frame_counter / (
                now - fps_time
            )

            frame_counter = 0

            fps_time = now

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        draw_ui(
            output,
            filter_name,
            active
        )

        cv2.putText(
            output,
            f"{fps:.0f} FPS",
            (
                w - 65,
                h - 8
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            .28,
            (120, 120, 120),
            1,
            cv2.LINE_AA
        )

        cv2.imshow(
            WINDOW_NAME,
            output
        )

        key = cv2.waitKey(1) & 0xFF

        if key == 27 or key == ord("q"):
            break

    camera.release()

    detector.close()

    cv2.destroyAllWindows()

    print()
    print("AR system stopped.")


if __name__ == "__main__":
    main()