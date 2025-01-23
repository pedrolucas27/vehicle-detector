from ultralytics import YOLO
import cv2
import cvzone
import math
from sort.sort import *
from mqtt.client import create_client, connect_client, publish_event

cap = cv2.VideoCapture("data/trafego_v2.mp4")
model = YOLO("models/yolov8n.pt")

tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

def load_coco_classes(coco_file="models/coco.names"):
    with open(coco_file, "r") as f:
        classes = f.read().strip().split("\n")
    return classes

coco_classes = load_coco_classes()
limits = [20, 600, 1250, 600]
seen_ids = set()
totalCount = []
veiculos_dic = {}

client = create_client()
connect_client(client)

while True:
    success, img = cap.read()
    results = model(img, stream=True)
    detections = np.empty((0, 5))
    current_class = ''
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            w, h = x2 - x1, y2 - y1
            conf = math.ceil((box.conf[0] * 100)) / 100

            cls = int(box.cls[0])
            current_class = coco_classes[cls]

            if current_class == 'car' or current_class == 'truck' or current_class == 'bus' or current_class == 'motorbike' and conf > 0.3:
                currentArray = np.array([x1, y1, x2, y2, conf])
                detections = np.vstack((detections, currentArray))

    resultsTracker = tracker.update(detections)
    cv2.line(img, (limits[0], limits[1]),(limits[2], limits[3]), (0, 0, 255), 5)

    for result in resultsTracker:
        x1, y1, x2, y2, id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 0))
        cvzone.putTextRect(img, f'{int(id)}', (max (0, x1), max(35, y1)), scale=2, thickness=1, offset=2)

        cx, cy = x1 + w // 2, y1 + h // 2
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        if limits[0] < cx < limits [2] and limits[1] - 30 < cy < limits[1] + 30:
            if totalCount.count(id) == 0:
                cv2.line(img, (limits[0], limits[1]),(limits[2], limits[3]), (0, 255, 0), 5)
                totalCount.append(id)
                publish_event(client, { "vec_id": int(id), "type": current_class, "timestamp": time.time() }, current_class)
                


    cvzone.putTextRect(img, f'Contador: {len(totalCount)}', (50, 50))

    if not success:
        break

    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # Pressionar 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(f"Dic {veiculos_dic}")
print(f"Total Count: {len(totalCount)}")
print(f"Total Set: {len(seen_ids)}")

