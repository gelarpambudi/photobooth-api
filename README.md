# PHOTOBOOTH API

---
## ENDPOINT LIST

- `/api/generate-image`
    - **Usage:** Process and generate result image
    - **Request Method:** `POST`
    - **Request parameter:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   tx_id        |  string      |
        |   BODY   |   frame_id        | string       |

        E.g.
        ```
        {
            "tx_id": "001122",
            "frame_id": 4
        }

        ```
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY   |   img_url   | list of string (`{BASE_URL}/static/res_image/{tx_id}/{effect}/1.png`) |
        |   BODY   |   gif_url   | list of string (`{BASE_URL}/static/res_image/{tx_id}/{effect}/compiled.gif`) |
        |   BODY   |   compiled_url   | list of string (`{BASE_URL}/static/res_image/{tx_id}/{effect}/compiled.jpg`) |
        |   BODY    | error | string |

        E.g.
        ```
        #ON SUCCESS
        {
            "status_code": 200,
            "message": "Success",
            "result_url": [
                http://localhost/static/res_image/123456/winter/compiled.jpg,
                http://localhost/static/res_image/123456/summer/compiled.jpg,
                http://localhost/static/res_image/123456/sepia/compiled.jpg
            ],
            "error": "null"
        }

        #ON FAILURE
        {
            "status_code": 503,
            "message": "Cannot process the image",
            "error": "Your python error message"
        }
        ```

- `/api/get-frame`
    - **Usage:** list available frame
    - **Request Method:** `GET`
    - **Request parameter:** None
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY   |   frame_list   | dict consists of `eight_frame_list`, `six_frame_list`, `six_frame_three_takes_list` keys |

        E.g.
        ```
        {
        "frame_list": {
            "eight_frame_list": [
            "http://localhost:8080/static/frame_assets/frame-1.png",
            "http://localhost:8080/static/frame_assets/frame-2.png",
            "http://localhost:8080/static/frame_assets/frame-3.png"
            ],
            "six_frame_list": [
            "http://localhost:8080/static/frame_assets/frame-5.png",
            "http://localhost:8080/static/frame_assets/frame-6.png",
            "http://localhost:8080/static/frame_assets/frame-7.png" 
            ]
        },
        "message": "Success",
        "status_code": 200
        }
        ```

- `/api/send-email`
    - **Usage:** Send final image and gif to email
    - **Request Method:** `POST`
    - **Request parameter:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   tx_id        |  string      |
        |   BODY   |   effect        | string       |
        |   BODY   |   email        | string       |
        |   BODY   |   recipient_name        | string       |

        E.g.
        ```
        {
            "tx_id": "001122",
            "effect": "winter",
            "email": "gelargelur@gmail.com",
            "recipient_name": "Gelar"
        }

        ```
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY    | error | string |

        E.g.
        ```
        #ON SUCCESS
        {
            "status_code": 200,
            "message": "Success",
            "error": "null"
        }

        #ON FAILURE
        {
            "status_code": 503,
            "message": "Failed to send email",
            "error": "Your python error message"
        }
        ```

- `/api/print-image`
    - **Usage:** Printe the chosen image
    - **Request Method:** `POST`
    - **Request parameter:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   tx_id        |  string      |
        |   BODY   |   effect        | string       |

        E.g.
        ```
        {
            "tx_id": "001122",
            "effect": "winter",
        }

        ```
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY    | error | string |

        E.g.
        ```
        #ON SUCCESS
        {
            "status_code": 200,
            "message": "Success",
            "error": "null"
        }

        #ON FAILURE
        {
            "status_code": 503,
            "message": "Failed to print email",
            "error": "Your python error message"
        }
        ```

- `/api/upload-image`
    - **Usage:** Upload the captured image
    - **Request Method:** `POST`
    - **Request parameter:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   HTTP FORM   |   tx_id        |  string      |
        |   HTTP FORM   |   img_file        | list of images       |
    - **Response:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY    | error | string |

        E.g.
        ```
        #ON SUCCESS
        {
            "status_code": 200,
            "message": "Success",
            "error": "null"
        }

        #ON FAILURE
        {
            "status_code": 503,
            "message": "Failed to upload email",
            "error": "Your python error message"
        }
        ```
