#include <opencv2/opencv.hpp>
#include <cpp_redis/cpp_redis>
#include <iostream>
#include <thread>
#include <chrono>
#include <vector>

#define REDIS_HOST "127.0.0.1"
#define REDIS_PORT 6379
#define FRAME_QUEUE "video_frames"

std::vector<unsigned char> encodeImg(const cv::Mat& frame) {
    std::vector<unsigned char> buffer;
    cv::imencode(".jpg", frame, buffer);
    return buffer;
}

void captureFrames() {
    cpp_redis::client redisClient;

    try {
        redisClient.connect(REDIS_HOST, REDIS_PORT);
    } catch (const std::exception& e) {
        std::cerr << "Redis bağlantısı başarısız: " << e.what() << std::endl;
        return;
    }

    cv::VideoCapture cap("/home/birdal/od-services/DJI_20241112160711_0002_V.mp4");
    if (!cap.isOpened()) {
        std::cerr << "Video açma hatası!" << std::endl;
        return;
    }

    int noFrameCount = 0;

    while (true) {
        cv::Mat frame;
        bool ret = cap.read(frame);

        if (!ret) {
            noFrameCount++;
            std::cout << "Kamera bağlantısı yok, bekleniyor..." << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            
            if (noFrameCount >= 5) {
                std::cout << "Kamera devre dışı, uyku moduna geçiliyor." << std::endl;
                std::this_thread::sleep_for(std::chrono::seconds(5));
            }

            continue;
        } else {
            noFrameCount = 0;  // Bağlantı sağlanırsa sayaç sıfırlanır
        }

        std::vector<unsigned char> imageBytes = encodeImg(frame);
        redisClient.lpush(FRAME_QUEUE, {imageBytes.begin(), imageBytes.end()});
        redisClient.commit();  // Asenkron işlemler için commit gerekebilir
    }

    cap.release();
}

int main() {
    captureFrames();
    return 0;
}
