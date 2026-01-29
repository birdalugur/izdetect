import torch
from transformers import DetrImageProcessorFast, DetrForObjectDetection
from core.utils import ProcessingTimer
import time

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"device: {device}")
processor = DetrImageProcessorFast.from_pretrained(
    "facebook/detr-resnet-50", revision="no_timm"
)
model = DetrForObjectDetection.from_pretrained(
    "facebook/detr-resnet-50", revision="no_timm"
).to(device)

model.half()


model.eval()

timer = ProcessingTimer()

batch_count = 1


def process_frame(frame):
    # zaten numpy array olarak alındığı için kaldırıldı.
    # image = Image.fromarray(frame)
    inputs = processor(images=frame, return_tensors="pt").to(
        device, dtype=torch.float16, non_blocking=True
    )
    with torch.no_grad:
        outputs = model(**inputs)
    target_sizes = torch.tensor([frame.shape[:2]]).to(device)
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=0.7
    )[0]

    if device == "cpu":
        results["scores"] = results["scores"].detach().cpu().numpy()
        results["boxes"] = results["boxes"].detach().cpu().numpy()
        results["labels"] = results["labels"].detach().cpu().numpy()

    del inputs
    del outputs
    if device == "cuda":
        torch.cuda.empty_cache()
    return results


def process_batch(frames):
    global batch_count
    """
    frames: list of numpy arrays of shape (height, width, 3)
    returns: a list of dictionaries with keys: dict_keys(['scores', 'labels', 'boxes']) containing detection results.
    """
    timer.start("processor")
    inputs = processor(images=frames, return_tensors="pt", device=device).to(
        device, dtype=torch.float16, non_blocking=True
    )
    timer.stop("processor")
    with torch.no_grad():
        s = time.time()
        timer.start("detection")
        outputs = model(**inputs)
        timer.stop("detection")
        print(f"detect time for batch {batch_count}: {(time.time() - s):.2f} seconds")
    timer.start("target")
    target_sizes = torch.tensor([frame.shape[:2] for frame in frames]).to(device)
    timer.stop("target")
    timer.start("post_process")
    results = processor.post_process_object_detection(
        outputs, threshold=0.7, target_sizes=target_sizes
    )
    timer.stop("post_process")
    batch_count += 1

    del outputs
    del inputs
    if device == "cuda":
        torch.cuda.empty_cache()

    return results


def get_label_name(label):
    return model.config.id2label[label.item()]
