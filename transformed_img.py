import pickle
import cv2
import numpy as np


def abs_sobel_thresh(img, orient='x', thresh_min=0, thresh_max=255):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if orient == 'x':
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    elif orient == 'y':
        sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    abs_sobel = np.absolute(sobel)
    scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
    bin_out = np.zeros_like(scaled_sobel)
    bin_out[(scaled_sobel >= thresh_min) & (scaled_sobel <= thresh_max)] = 1
    return bin_out


def color_select(img, sthresh=(0, 255), vthresh=(0, 255)):
    hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    s = hls[:, :, 2]
    s_bin = np.zeros_like(s)
    s_bin[(s > sthresh[0]) & (s <= sthresh[1])] = 1

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    v = hsv[:, :, 2]
    v_bin = np.zeros_like(v)
    v_bin[(v >= vthresh[0]) & (v <= vthresh[1])] = 1

    out = np.zeros_like(s)
    out[(s_bin == 1) & (v_bin == 1)] = 1
    return out


def warp_image(img):
    """
    Applying filters to find lane lines
    and warping the image
    :param img: initial image
    :return result: warped binary image
    """
    dist_pickle = pickle.load(open('./calibration_pickle.p', 'rb'))
    mtx = dist_pickle['mtx']
    dist = dist_pickle['dist']

    img = cv2.undistort(img, mtx, dist, None, mtx)

    # write_name = './test_images/undistorted'+str(idx)+'.jpg'
    # cv2.imwrite(write_name, img)

    detect_lines = np.zeros_like(img[:, :, 0])
    gradx = abs_sobel_thresh(img, orient='x', thresh_min=20)
    grady = abs_sobel_thresh(img, orient='y', thresh_min=25)
    color = color_select(img, sthresh=(110, 255), vthresh=(50, 255))

    # Using color selecting and sobel to extrapolate lanes
    detect_lines[(gradx == 1) & (grady == 1) | (color == 1)] = 255

    # write_name = './test_images/line_detected'+str(idx)+'.jpg'
    # cv2.imwrite(write_name, detect_lines)

    w = img.shape[1]
    h = img.shape[0]
    src = np.float32([[230, 720], [1100, 720], [580, 460], [700, 460]])
    offset = w*0.25
    dst = np.float32([[offset, h], [w-offset, h], [offset, 0], [w-offset, 0]])

    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    # Changing perspective to effectively look for lane lines
    binary_warped = cv2.warpPerspective(detect_lines, M, (w, h), flags=cv2.INTER_LINEAR)
    # write_name = './test_images/warped'+str(idx)+'.jpg'
    # cv2.imwrite(write_name, binary_warped)
    return binary_warped, M, Minv
