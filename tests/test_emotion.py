import init;

from app.pipeline import DHPipeline;

init.init_path();

if __name__ == '__main__':
    pipeline = DHPipeline();
    text = "你叫什么名字?";
    answer, emotion_score = pipeline.generate_response(text);
    print(f"回答: {answer}\n 情感分数: {emotion_score}");