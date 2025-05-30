from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import time

app = Client("my_math_bot")

# Game state storage
user_sessions = {}
active_questions = {}

def generate_problem(difficulty="Easy"):
    """Generate math problem based on difficulty"""
    difficulties = {
        "Easy": {"ops": ['+', '-'], "range": (1, 20)},
        "Medium": {"ops": ['+', '-', '*'], "range": (1, 50)},
        "Hard": {"ops": ['+', '-', '*', '/'], "range": (1, 100)}
    }
    
    config = difficulties[difficulty]
    op = random.choice(config["ops"])
    min_num, max_num = config["range"]
    
    if op == '+':
        a, b = random.randint(min_num, max_num), random.randint(min_num, max_num)
        ans = a + b
    elif op == '-':
        a = random.randint(min_num + 5, max_num)
        b = random.randint(min_num, a - 1)
        ans = a - b
    elif op == '*':
        a, b = random.randint(1, 12), random.randint(1, 12)
        ans = a * b
    else:  # division
        b = random.randint(1, 10)
        ans = random.randint(1, 10)
        a = b * ans
    
    return f"{a} {op} {b} = ?", ans

def create_menu(user_id):
    """Create the initial menu"""
    buttons = [
        [
            InlineKeyboardButton("5Qs", callback_data=f"count_{user_id}_5"),
            InlineKeyboardButton("10Qs", callback_data=f"count_{user_id}_10"),
            InlineKeyboardButton("15Qs", callback_data=f"count_{user_id}_15")
        ],
        [
            InlineKeyboardButton("Easy", callback_data=f"diff_{user_id}_Easy"),
            InlineKeyboardButton("Medium", callback_data=f"diff_{user_id}_Medium"),
            InlineKeyboardButton("Hard", callback_data=f"diff_{user_id}_Hard")
        ],
        [InlineKeyboardButton("Start Game", callback_data=f"start_{user_id}")]
    ]
    
    text = "Let's start the Math Game!\n\nChoose difficulty and number of questions:"
    
    return text, InlineKeyboardMarkup(buttons)

def create_question(user_id):
    """Generate a question with answer buttons"""
    session = user_sessions[user_id]
    problem, answer = generate_problem(session["difficulty"])
    
    # Generate wrong answers
    answers = {answer}
    while len(answers) < 3:
        offset = random.choice([-3, -2, -1, 1, 2, 3])
        wrong = max(1, answer + offset)
        answers.add(wrong)
    
    answers = list(answers)[:3]
    random.shuffle(answers)
    
    # Store correct answer
    q_num = session.get("current_q", 0) + 1
    active_questions[user_id] = {
        "answer": answer,
        "message_id": None,
        "q_num": q_num
    }
    session["current_q"] = q_num
    
    # Create buttons
    buttons = [
        [InlineKeyboardButton(str(ans), callback_data=f"ans_{user_id}_{ans}") 
        for ans in answers]
    ]
    buttons.append([InlineKeyboardButton("Stop", callback_data=f"stop_{user_id}")])
    
    text = (
        f"Maths Master Challenge!\n\n"
        f"Level: {session['difficulty']}\n"
        f"Q: {q_num} / {session['max_questions']}\n\n"
        f"Solve: {problem}\n\n"
        f"Think fast, choose wisely!"
    )
    
    return text, InlineKeyboardMarkup(buttons)

@app.on_message(filters.command("math"))
async def start_math(client, message):
    user_id = message.from_user.id
    text, markup = create_menu(user_id)
    
    # Clear any existing session
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    await message.reply_text(text, reply_markup=markup)

@app.on_callback_query()
async def handle_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    try:
        # Handle difficulty selection
        if data.startswith("diff_"):
            _, _, target_user_id, difficulty = data.split('_')
            if int(target_user_id) != user_id:
                await callback_query.answer("This menu isn't for you!")
                return
                
            if user_id not in user_sessions:
                user_sessions[user_id] = {"correct": 0, "total": 0}
            user_sessions[user_id]["difficulty"] = difficulty
            text, markup = create_menu(user_id)
            await callback_query.edit_message_text(text, reply_markup=markup)
            await callback_query.answer(f"Difficulty set to {difficulty}")
            return
        
        # Handle question count selection
        elif data.startswith("count_"):
            _, _, target_user_id, count = data.split('_')
            if int(target_user_id) != user_id:
                await callback_query.answer("This menu isn't for you!")
                return
                
            if user_id not in user_sessions:
                user_sessions[user_id] = {"correct": 0, "total": 0}
            user_sessions[user_id]["max_questions"] = int(count)
            text, markup = create_menu(user_id)
            await callback_query.edit_message_text(text, reply_markup=markup)
            await callback_query.answer(f"Set to {count} questions")
            return
        
        # Handle game start
        elif data.startswith("start_"):
            if user_id not in user_sessions or "difficulty" not in user_sessions[user_id]:
                await callback_query.answer("Please select difficulty first")
                return
            if "max_questions" not in user_sessions[user_id]:
                user_sessions[user_id]["max_questions"] = 5  # Default
            
            text, markup = create_question(user_id)
            msg = await callback_query.edit_message_text(text, reply_markup=markup)
            active_questions[user_id]["message_id"] = msg.id
            return
        
        # Handle answer selection
        elif data.startswith("ans_"):
            _, _, target_user_id, answer = data.split('_')
            if int(target_user_id) != user_id:
                await callback_query.answer("This question isn't for you!")
                return
                
            answer = int(answer)
            
            if user_id not in active_questions:
                await callback_query.answer("Session expired. Start new game with /math")
                return
            
            session = user_sessions[user_id]
            correct_answer = active_questions[user_id]["answer"]
            is_correct = (answer == correct_answer)
            
            # Update stats
            session["total"] += 1
            if is_correct:
                session["correct"] += 1
                feedback = "✅ Correct!"
            else:
                feedback = f"❌ Wrong! Answer was {correct_answer}"
            
            # Check if game should continue
            if session["current_q"] >= session["max_questions"]:
                # Game over
                accuracy = (session["correct"] / session["total"]) * 100
                text = (
                    f"Game Over!\n\n"
                    f"Final Score: {session['correct']}/{session['total']}\n"
                    f"Accuracy: {accuracy:.1f}%\n\n"
                    f"Play again with /math"
                )
                await callback_query.edit_message_text(text)
                del user_sessions[user_id]
                del active_questions[user_id]
            else:
                # Next question
                text, markup = create_question(user_id)
                await callback_query.edit_message_text(
                    text=f"{feedback}\n\n{text}",
                    reply_markup=markup
                )
                active_questions[user_id]["message_id"] = callback_query.message.id
            
            await callback_query.answer()
            return
        
        # Handle stop button
        elif data.startswith("stop_"):
            if user_id in user_sessions:
                session = user_sessions[user_id]
                accuracy = (session["correct"] / session["total"]) * 100 if session["total"] > 0 else 0
                text = (
                    f"Game Stopped\n\n"
                    f"Score: {session['correct']}/{session['total']}\n"
                    f"Accuracy: {accuracy:.1f}%\n\n"
                    f"Play again with /math"
                )
                await callback_query.edit_message_text(text)
                del user_sessions[user_id]
                if user_id in active_questions:
                    del active_questions[user_id]
            else:
                await callback_query.edit_message_text("Game stopped. Play again with /math")
            await callback_query.answer()
    
    except Exception as e:
        print(f"Error handling callback: {e}")
        await callback_query.answer("An error occurred")

app.run()
