from argument_parser import get_args
import cv2
from datetime import datetime

# =========================================================================================
#       CONSTANTS
# =========================================================================================


CV2_WINDOW_NAME = "camera stream"


# =========================================================================================
#       MAIN VIDEO RECORDING LOOP
# =========================================================================================


def main():
    """
    This function opens a camera stream using OpenCV and write the video to a file.
    """
    # Parse the arguments / get the settings.
    args = get_args()

    # Check the arguments.
    if (
        args.square
        and (args.width is not None and args.height is not None)
        and (args.width != args.height)
    ):
        print(
            "If '--square' is set together with '--width' and '--height', the values of width and height have to match."
            + "(or set only width or only height)"
        )
        print(f"(parsed values: width = {args.width}, height = {args.height})")
        return

    if args.width is not None and args.width < 1:
        print(
            "The value set using '--width' is too small. Use a width of at least one pixel."
        )
        return

    if args.height is not None and args.height < 1:
        print(
            "The value set using '--height' is too small. Use a height of at least one pixel."
        )
        return

    # If the image has to be square and only width or only height were given,
    # set the given value also for the other parameter.
    if args.square and args.width is not None and args.height is None:
        args.height = args.width
    if args.square and args.height is not None and args.width is None:
        args.width = args.height

    # Open the camera stream and the window.
    cv2.namedWindow(CV2_WINDOW_NAME)
    video_capture = cv2.VideoCapture(args.device_id)
    video_writer = None

    if video_capture.isOpened():
        # Capture the first image.
        ret, _ = video_capture.read()
        while ret:
            # Capture the image.
            ret, frame = video_capture.read()

            # Square?
            if args.square:
                height, width, _ = frame.shape
                if width > height:
                    frame = frame[
                        :,
                        int((width - height) / 2) : int((width - height) / 2) + height,
                        :,
                    ]
                elif height < width:
                    frame = frame[
                        int((height - width) / 2) : int((height - width) / 2) + width,
                        :,
                        :,
                    ]
                else:
                    # Already square.
                    pass

            # Resize?
            if args.width is not None or args.height is not None:
                height_curr, width_curr, _ = frame.shape
                frame = cv2.resize(
                    frame,
                    (
                        args.width if args.width is not None else width_curr,
                        args.height if args.height is not None else height_curr,
                    ),
                    interpolation=cv2.INTER_AREA,
                )

            # Display the camera stream.
            cv2.imshow(CV2_WINDOW_NAME, frame)

            # Write the frame to the video?
            if video_writer is not None:
                video_writer.write(frame)

            # Input handling.
            key = cv2.waitKey(30)
            if key == 27 or key == ord("q"):
                # Exit on ESC or q.
                print("Exit program.")
                break
            elif key == 32:
                # Start / stop video recording on SPACE.
                if video_writer is None:
                    # Start recording.
                    filename = (
                        f"{datetime.now().year}{datetime.now().month:02d}{datetime.now().day:02d}"
                        + f"{datetime.now().hour:02d}{datetime.now().minute:02d}{datetime.now().second:02d}_recording.mp4"
                    )
                    height, width, _ = frame.shape
                    video_writer = cv2.VideoWriter(
                        filename, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (width, height)
                    )
                    video_writer.write(frame)
                    print(f"Started recording to '{filename}'.")
                else:
                    # Stop recording.
                    video_writer.release()
                    video_writer = None
                    print("Stopped recording. Video written.")
            elif key == ord("s"):
                # Save a picture on s.
                filename = (
                    f"{datetime.now().year}{datetime.now().month:02d}{datetime.now().day:02d}"
                    + f"{datetime.now().hour:02d}{datetime.now().minute:02d}{datetime.now().second:02d}_frame.png"
                )
                cv2.imwrite(filename, frame)
                print(f"Frame written to '{filename}'.")

    else:
        print("Cannot open video stream.")

    # Terminate the windows and the camera stream. If we are still recording, stop the recording.
    if video_writer is not None:
        # Stop recording.
        video_writer.release()
        video_writer = None
        print("Stopped recording. Video written.")
    cv2.destroyWindow(CV2_WINDOW_NAME)
    video_capture.release()


# =========================================================================================
#       MAIN
# =========================================================================================

if __name__ == "__main__":
    main()
