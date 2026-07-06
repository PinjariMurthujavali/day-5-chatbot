# ============================================
# Day 5: Chat Analysis + Sentiment + JSON Export
# ============================================

import os
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime
import sys
import json
# ↑ "json" → Python objects ni JSON format lo convert చేయడానికి
# (universal data format, सب platforms understand చేస్తాయి)

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


# STEP 1: Personalities Dictionary (Day 4 నుండే same)
personalities = {
    "mentor": "You are a friendly, motivating coding mentor who explains things simply and encourages the user like a supportive friend.",
    "comedian": "You are a witty, funny comedian who makes jokes and uses humor while still being helpful. Keep responses light and entertaining.",
    "strict_teacher": "You are a strict but fair teacher who doesn't tolerate nonsense. Be direct, no-nonsense, and demand excellence.",
    "zen_master": "You are a calm, wise zen master who speaks in philosophical terms and uses metaphors.",
    "enthusiast": "You are an overly enthusiastic tech enthusiast who gets excited about everything! Use lots of emojis and exclamation marks.",
}

default_personality = "mentor"
selected_personality = default_personality

if len(sys.argv) > 1:
    requested_personality = sys.argv[1].lower()
    if requested_personality in personalities:
        selected_personality = requested_personality
        print(f"✅ Personality selected: {selected_personality.upper()}\n")
    else:
        print(f"❌ Personality '{requested_personality}' not found!")
        print(f"Available: {', '.join(personalities.keys())}\n")

system_prompt = personalities[selected_personality]
conversation_history = [{"role": "system", "content": system_prompt}]

personality_emoji = {
    "mentor": "🎓", "comedian": "🤣", "strict_teacher": "👨‍🏫",
    "zen_master": "🧘", "enthusiast": "🤩",
}

print(f"{personality_emoji.get(selected_personality, '🤖')} AI Chatbot ({selected_personality.upper()}) Ready!")
print("Type 'exit' to end chat, analyze, and save.\n")


# STEP 2: ANALYSIS FUNCTIONS (NEW!)

def analyze_sentiment(text):
    # ↑ Simple sentiment analysis (basic version)
    # Real applications use ML models, kani idi educational approach
    
    positive_words = ["good", "great", "amazing", "awesome", "excellent", "love", "best", "perfect", "brilliant"]
    negative_words = ["bad", "terrible", "awful", "hate", "worst", "poor", "useless", "stupid", "wrong"]
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    # ↑ positive_words list లో ఉన్న words count చేస్తుంది
    # negative_words list లో ఉన్న words count చేస్తుంది
    
    if pos_count > neg_count:
        return "positive", pos_count
    elif neg_count > pos_count:
        return "negative", neg_count
    else:
        return "neutral", 0


def get_statistics(conversation_history):
    # ↑ Conversation నుండి stats extract చేయడం
    
    stats = {
        "total_messages": 0,
        "user_messages": 0,
        "ai_messages": 0,
        "total_words": 0,
        "total_characters": 0,
        "avg_user_message_length": 0,
        "avg_ai_response_length": 0,
        "sentiment_breakdown": {"positive": 0, "negative": 0, "neutral": 0},
    }
    
    user_words = []
    ai_words = []
    
    for message in conversation_history:
        # ↑ Conversation లోని prathi message మీద loop run చేస్తుంది
        
        if message["role"] == "system":
            continue
            # ↑ System prompt skip చేస్తుంది (analysis కోసం needed కాదు)
        
        content = message["content"]
        words = content.split()
        # ↑ .split() → text ni words లోకి break చేస్తుంది
        # "hello world" → ["hello", "world"]
        
        stats["total_messages"] += 1
        stats["total_words"] += len(words)
        stats["total_characters"] += len(content)
        
        sentiment, _ = analyze_sentiment(content)
        stats["sentiment_breakdown"][sentiment] += 1
        
        if message["role"] == "user":
            stats["user_messages"] += 1
            user_words.extend(words)
            # ↑ .extend() → list ni list లో merge చేస్తుంది
        else:  # assistant
            stats["ai_messages"] += 1
            ai_words.extend(words)
    
    # Calculate averages
    if stats["user_messages"] > 0:
        stats["avg_user_message_length"] = stats["total_words"] // stats["user_messages"] // 2
        # ↑ Rough estimate (total words / user messages)
    
    if stats["ai_messages"] > 0:
        stats["avg_ai_response_length"] = stats["total_words"] // stats["ai_messages"] // 2
    
    return stats


def get_top_keywords(conversation_history, top_n=10):
    # ↑ Most frequent words ni find చేయడం
    # top_n = show చేయాల్సిన top keywords count
    
    stop_words = {"the", "a", "is", "it", "to", "and", "or", "in", "on", "at", "for", "of", "with", "you", "i"}
    # ↑ Common words (ignored చేస్తాం) - meaningful కాబట్టి
    
    word_freq = {}
    
    for message in conversation_history:
        if message["role"] == "system":
            continue
        
        words = message["content"].lower().split()
        # ↑ lowercase గా convert చేస్తుంది (case-insensitive counting)
        
        for word in words:
            # Remove punctuation
            word = word.strip(".,!?;:")
            
            if word not in stop_words and len(word) > 2:
                # ↑ Stop words + చిన్న words skip చేస్తుంది
                word_freq[word] = word_freq.get(word, 0) + 1
                # ↑ .get(word, 0) → word ఉందా check చేసి, లేకపోతే 0 return చేస్తుంది
    
    # Sort by frequency
    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    # ↑ sorted() → frequency order లో sort చేస్తుంది
    # lambda → temporary function (just for sorting)
    # [:top_n] → first top_n items ni matrame తీసుకుంటుంది
    
    return top_keywords


# STEP 3: Main Chat Loop (Day 4 లాగే same)

while True:
    user_question = input("Nీ question enti? : ")

    if user_question.lower() == "exit":
        # STEP 4: ANALYSIS + SAVE చేయడం
        
        print("\n" + "="*50)
        print("📊 CHAT ANALYSIS")
        print("="*50 + "\n")
        
        # Get all analysis
        stats = get_statistics(conversation_history)
        keywords = get_top_keywords(conversation_history, top_n=10)
        
        # Print stats
        print(f"📈 Statistics:")
        print(f"   Total Messages: {stats['total_messages']}")
        print(f"   User Messages: {stats['user_messages']}")
        print(f"   AI Responses: {stats['ai_messages']}")
        print(f"   Total Words: {stats['total_words']}")
        print(f"   Total Characters: {stats['total_characters']}")
        print()
        
        print(f"😊 Sentiment Breakdown:")
        print(f"   Positive: {stats['sentiment_breakdown']['positive']}")
        print(f"   Negative: {stats['sentiment_breakdown']['negative']}")
        print(f"   Neutral: {stats['sentiment_breakdown']['neutral']}")
        print()
        
        print(f"🔑 Top Keywords:")
        for keyword, count in keywords:
            print(f"   {keyword}: {count} times")
        print()
        
        # STEP 5: Save to JSON File
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        analysis_data = {
            "metadata": {
                "personality": selected_personality,
                "timestamp": timestamp,
                "duration": f"{stats['total_messages']} messages",
            },
            "statistics": stats,
            "top_keywords": [{"word": word, "frequency": count} for word, count in keywords],
        }
        # ↑ Dictionary format lo analysis organize చేస్తుంది
        # JSON లో export చేయడానికి ready
        
        filename = f"chat_analysis_{selected_personality}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(analysis_data, file, indent=2, ensure_ascii=False)
            # ↑ json.dump() → Python dictionary ni JSON file lo write చేస్తుంది
            # indent=2 → readable formatting (pretty print)
            # ensure_ascii=False → emojis/Unicode chars support
        
        print(f"💾 Analysis saved to: {filename}\n")
        print("Chat end ayyindi. Bye bro! 👋")
        break

    conversation_history.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation_history
    )

    ai_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": ai_reply})

    print("\nAI Answer:", ai_reply, "\n")