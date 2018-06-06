# -*- coding: utf-8 -*-
picamera={"resolution":(800,600),"framerate":30,"format":"bgr"}

hsv_rose={"low":(153, 10, 10),"high":(173, 255,255),"team":"rose"}
hsv_green={"low":(20, 10, 10),"high":(40, 255,255),"team":"green"}
hsv_blue={"low":(87, 10, 10),"high":(107, 255,255),"team":"blue"}
hsv_ball={"low":(167, 50, 0),"high":(187, 255,255),"team":"ball"}

parameters_fields_ld={"canny_min_threshold":150, "canny_max_threshold":300, "threshold_min":150, "threshold_max":255, "erode_iter":2, "dilate_iter":4, "number_pixels_per_field":5000 }

parameters_thymio_ld={"threshold_min":100, "threshold_max":255, "number_pixels_per_field":150, "min_radius":8.5}

parameters_dots_ld={"threshold_min":100, "threshold_max":255, "number_pixels_per_field":5}

parameters_redis={"host":"localhost","port":6379}

save_images = False