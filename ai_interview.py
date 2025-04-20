import os
import random
import time
import tempfile
import speech_recognition as sr
from gtts import gTTS
from dotenv import load_dotenv
import google.generativeai as genai
import pygame  # Add this

# --- Configuration ---
load_dotenv() # Load environment variables from .env file

# Configure Google AI (Gemini)
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Create a .env file.")
    genai.configure(api_key=GOOGLE_API_KEY)
    # Select the Gemini model (e.g., 'gemini-pro')
    ai_model = genai.GenerativeModel('gemini-pro')
    print("Google AI SDK Configured.")
    USE_AI_FEEDBACK = True
except Exception as e:
    print(f"ERROR: Failed to configure Google AI SDK: {e}")
    print("AI feedback and follow-up questions will be disabled.")
    ai_model = None
    USE_AI_FEEDBACK = False

# --- Interview Questions ---
# Add more diverse questions (behavioral, technical, situational)
QUESTIONS = [
    {"text": "Tell me about yourself.", "type": "General", "format": None},
    {"text": "What are your biggest strengths?", "type": "General", "format": None},
    {"text": "What are your biggest weaknesses?", "type": "General", "format": None},
    {"text": "Describe a challenging project you worked on and how you handled it. Please use the STAR method.", "type": "Behavioral", "format": "STAR"},
    {"text": "Where do you see yourself in 5 years?", "type": "General", "format": None},
    {"text": "Why are you interested in this type of role?", "type": "General", "format": None},
    {"text": "Tell me about a time you had a conflict with a coworker.", "type": "Behavioral", "format": None},
    {"text": "Explain the difference between a list and a tuple in Python.", "type": "Technical", "format": None},
    {"text": "What is Object-Oriented Programming?", "type": "Technical", "format": None},
]

# --- Helper Functions ---

def speak(text):
    """Converts text to speech and plays it using gTTS and pygame."""
    if not text:
        return
    try:
        print(f"\nAI Interviewer: {text}")
        tts = gTTS(text=text, lang='en', slow=False)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            temp_filename = fp.name
        tts.save(temp_filename)

        # Initialize and play with pygame
        pygame.mixer.init()
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        os.remove(temp_filename)
        time.sleep(0.5)

    except Exception as e:
        print(f"Error during text-to-speech: {e}")
        print(" ---> (Speaking skipped)")

def listen():
    """Listens via microphone and returns recognized text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        r.pause_threshold = 1.2 # Slightly longer pause allowed
        r.energy_threshold = 400 # Adjust if recognition is too sensitive/insensitive
        # Listen for the first phrase and extract it into audio data
        try:
            # Adjust for ambient noise dynamically
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=7, phrase_time_limit=45) # 7s silence timeout, 45s max phrase
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Let's move on.")
            return None
        except Exception as e:
            print(f"Error obtaining audio: {e}")
            return None

    # Recognize speech using Google Web Speech API (requires internet)
    try:
        print("Recognizing...")
        text = r.recognize_google(audio)
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand that.")
        return None
    except sr.RequestError as e:
        speak(f"Could not request results from the speech recognition service. {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during speech recognition: {e}")
        return None

def get_ai_feedback_and_followup(question_data, answer):
    """Gets feedback and a follow-up question from Google Gemini."""
    if not USE_AI_FEEDBACK or not ai_model or not answer:
        print("--> Skipping AI feedback generation.")
        # Provide a generic transition if AI is off or answer is missing
        return "Okay, let's proceed.", None

    question_text = question_data['text']
    question_type = question_data['type']
    expected_format = question_data['format']

    prompt = f"""
    You are an expert AI Mock Interviewer. Your tone is professional and encouraging.
    The candidate was asked the following '{question_type}' question:
    "{question_text}"

    The candidate provided this answer:
    "{answer}"
    """

    if expected_format == "STAR":
        prompt += f"\nEvaluate the answer based on the STAR method (Situation, Task, Action, Result). Note if elements seem missing or could be clearer."
    elif question_type == "Technical":
        prompt += f"\nEvaluate the technical accuracy, depth, and clarity of the explanation."
    else: # General/Behavioral without specific format
        prompt += f"\nEvaluate the clarity, relevance, and impact of the answer."

    prompt += """

    Provide concise, constructive feedback (1-3 sentences). Start the feedback with "Feedback:".
    Then, ask ONE relevant follow-up question to probe deeper into their answer or explore a related area. Start the follow-up question with "Follow-up:". If the answer is too brief or vague for a specific follow-up, ask a related standard question within the same '{question_type}' category.

    Ensure your entire response contains ONLY the "Feedback:" line and the "Follow-up:" line.
    Example:
    Feedback: That's a good start, but perhaps you could elaborate more on the specific results of your actions.
    Follow-up: Can you quantify the impact your contribution had on the project's success?
    """

    print("--> Asking Gemini for feedback...")
    try:
        # Generate content using the Gemini model
        response = ai_model.generate_content(prompt)

        # Basic check for blocked content (can refine with safety settings)
        if not response.candidates or not response.candidates[0].content.parts:
             if response.prompt_feedback.block_reason:
                 print(f"WARN: Gemini response blocked due to: {response.prompt_feedback.block_reason}")
                 return "My response was blocked due to safety settings. Let's move to the next question.", None
             else:
                 print("WARN: Gemini returned an empty response.")
                 return "I couldn't generate feedback for that response. Let's continue.", None


        content = response.text
        # print(f"DEBUG: Raw Gemini Response:\n{content}") # Uncomment for debugging

        # --- Parse the response ---
        feedback = "Okay." # Default feedback
        follow_up = None # Default no follow-up

        lines = content.strip().split('\n')
        found_feedback = False
        found_followup = False
        for line in lines:
            line_lower = line.lower()
            if line_lower.startswith("feedback:") and not found_feedback:
                feedback = line.split(":", 1)[1].strip()
                found_feedback = True
            elif line_lower.startswith("follow-up:") or line_lower.startswith("follow up:") and not found_followup:
                 # Handle potential variations like "Follow up:"
                follow_up = line.split(":", 1)[1].strip()
                found_followup = True

        # If parsing failed somehow, use generic transition
        if not found_feedback and not found_followup and len(content) > 10:
             print("WARN: Could not parse feedback/follow-up structure from Gemini response. Using generic transition.")
             feedback = "Interesting. Let's move on to the next topic."
             follow_up = None # Ensure no accidental follow-up
        elif not follow_up:
             # If feedback was found but no follow-up, create a transition
             feedback += " Let's move to the next question."

        return feedback, follow_up

    except Exception as e:
        print(f"ERROR interacting with Google AI: {e}")
        return "I encountered an error processing that. Let's move to the next question.", None


# --- Main Interview Loop ---

def run_interview():
    """Runs the main mock interview flow in the terminal."""
    speak("Hello! Welcome to your AI-powered mock interview.")
    time.sleep(0.5)
    speak("I will ask you a series of questions. Please answer clearly after the beep sound would normally be... just kidding, answer after I stop talking.")
    time.sleep(1)

    # Select a subset of questions for this session
    num_questions = min(len(QUESTIONS), 5) # Ask up to 5 base questions
    interview_deck = random.sample(QUESTIONS, k=num_questions)
    question_index = 0
    current_question_data = None # Stores dict of the question being asked

    while question_index < len(interview_deck) or current_question_data:
        # Decide what question to ask: follow-up or next from deck
        if current_question_data is None: # If no follow-up pending, get next from deck
            if question_index < len(interview_deck):
                current_question_data = interview_deck[question_index]
            else:
                # Should not happen if loop condition is correct, but safety break
                 break

        # Ask the question (either original or follow-up)
        speak(current_question_data['text'])

        # Get user's answer
        answer = listen()

        if answer:
            # Get feedback and potential follow-up from AI
            feedback_text, follow_up_text = get_ai_feedback_and_followup(current_question_data, answer)

            # Deliver feedback
            speak(feedback_text)

            # Prepare for next iteration
            if follow_up_text:
                # Ask the AI's follow-up question next
                # Create a temporary question dict for the follow-up
                current_question_data = {
                    "text": follow_up_text,
                    "type": current_question_data['type'], # Assume follow-up is same type
                    "format": None # Follow-ups generally don't have strict formats
                }
                # Don't increment question_index, the follow-up takes priority
            else:
                # No follow-up generated, move to the next question in the original deck
                current_question_data = None
                question_index += 1
        else:
            # If listen() failed or returned None (e.g., timeout, unintelligible)
            # Move to the next question in the deck without feedback
            speak("Okay, let's try a different question then.")
            current_question_data = None
            question_index += 1

        time.sleep(1) # Pause before the next interaction

    speak("That concludes our mock interview session. Thank you for participating! Remember to reflect on the feedback.")

if __name__ == "__main__":
    run_interview()