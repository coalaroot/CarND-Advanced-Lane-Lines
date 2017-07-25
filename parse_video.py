from moviepy.editor import VideoFileClip
from Lane import Line
from find_lanes import *
from transformed_img import warp_image


def process_image(img):
    warped_binary, M, Minv = warp_image(img)

    if Left.detected:
        Left.allx, Left.ally, \
        Left.current_fit, Left.detected = find_lanes(warped_binary, Left.current_fit,
                                                     Right.current_fit, left=True)

    if Right.detected:
        Right.allx, Right.ally, \
        Right.current_fit, Right.detected = find_lanes(warped_binary, Left.current_fit,
                                                       Right.current_fit, right=True)

    if not Right.detected:
        Right.allx, Right.ally, \
        Right.current_fit, Right.detected = find_lanes_from_scratch(warped_binary, right=True)

    if not Left.detected:
        Left.allx, Left.ally, \
        Left.current_fit, Left.detected = find_lanes_from_scratch(warped_binary, left=True)

    # Calculate curvature & distance from the center
    left_curv, right_curv = find_curvature(Left.ally, Left.allx, Right.ally, Right.allx)
    car_pos = car_position(Left.allx[-1], Right.allx[-1])

    # Create an image to draw the lines on
    warp_zero = np.zeros_like(warped_binary).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

    # Recast the x and y points into usable format for cv2.fillPoly()
    pts_left = np.array([np.transpose(np.vstack([Left.allx, Left.ally]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([Right.allx, Right.ally])))])
    pts = np.hstack((pts_left, pts_right))

    # Draw the lane onto the warped blank image
    cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))

    # Warp the blank back to original image space using inverse perspective matrix (Minv)
    newwarp = cv2.warpPerspective(color_warp, Minv, (img.shape[1], img.shape[0]))
    # Combine the result with the original image
    result = cv2.addWeighted(img, 1, newwarp, 0.3, 0)

    # Draw curvature & distance on the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    str1 = str('distance from center: ' + str(round(car_pos, 2)) + 'cm')
    str2 = str('lane curvatures: ' + str(round(left_curv, 3)) + "m & " + str(round(right_curv, 3)) + "m")
    cv2.putText(result, str1, (430, 630), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(result, str2, (230, 670), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # plt.imshow(result)
    # plt.show()
    return result


Left = Line()
Right = Line()
parsed_video = 'output_video.mp4'
clip1 = VideoFileClip("project_video.mp4")
parsed_clip = clip1.fl_image(process_image)
parsed_clip.write_videofile(parsed_video, audio=False)
