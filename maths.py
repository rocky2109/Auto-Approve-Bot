import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler

class MathGame:
    def __init__(self):
        self.user_stats = {}  # {user_id: {"correct": int, "total": int, "streak": int}}
        self.active_games = {}  # {user_id: {"answer": int, "message_id": int, "q_num": int}}

    def generate_problem(self, difficulty="medium"):
        """Generate math problem with answer based on difficulty"""
        difficulties = {
            "easy": {"ops": ['+', '-'], "range": (1, 20)},
            "medium": {"ops": ['+', '-', '*'], "range": (1, 30)},
            "hard": {"ops": ['+', '-', '*', '/'], "range": (1, 50)}
        }
        
        config = difficulties.get(difficulty, difficulties["medium"])
        op = random.choice(config["ops"])
        min_num, max_num = config["range"]
        
        if op == '+':
            a, b = random.randint(min_num, max_num), random.randint(min_num, max_num)
            ans = a + b
        elif op == '-':
            a = random.randint(min_num * 2, max_num)
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

    def create_question(self, user_id, difficulty="medium"):
        """Prepare new question with inline buttons"""
        # Initialize user stats if needed
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {"correct": 0, "total": 0, "streak": 0}
        
        # Generate problem and wrong answers
        problem, answer = self.generate_problem(difficulty)
        answers = {answer}
        
        while len(answers) < 4:
            offset = random.choice([-3, -2, -1, 1, 2, 3])
            wrong = max(1, answer + offset)
            answers.add(wrong)
        
        answers = list(answers)[:4]
        random.shuffle(answers)
        
        # Update active game
        q_num = self.active_games.get(user_id, {}).get("q_num", 0) + 1
        self.active_games[user_id] = {
            "answer": answer,
            "q_num": q_num,
            "start_time": time.time()
        }
        
        # Create buttons
        buttons = [
            [InlineKeyboardButton(str(ans), callback_data=f"math_{user_id}_{ans}")]
            for ans in answers
        ]
        
        # Add difficulty selector
        buttons.append([
            InlineKeyboardButton("Easy", callback_data=f"diff_{user_id}_easy"),
            InlineKeyboardButton("Medium", callback_data=f"diff_{user_id}_medium"),
            InlineKeyboardButton("Hard", callback_data=f"diff_{user_id}_hard")
        ])
        
        return (
            f"🧮 Question {q_num}\n\n{problem}\n\n"
            f"Score: {self.user_stats[user_id]['correct']}/{self.user_stats[user_id]['total']} "
            f"(Streak: {self.user_stats[user_id]['streak']})",
            InlineKeyboardMarkup(buttons)
        )

    def start_game(self, update: Update, context: CallbackContext):
        """Handle /math command"""
        user_id = update.effective_user.id
        text, markup = self.create_question(user_id)
        
        msg = update.message.reply_text(text, reply_markup=markup)
        self.active_games[user_id]["message_id"] = msg.message_id

    def handle_answer(self, update: Update, context: CallbackContext):
        """Process inline button answers"""
        query = update.callback_query
        user_id = query.from_user.id
        data = query.data
        
        # Handle difficulty change
        if data.startswith("diff_"):
            _, _, user_id, difficulty = data.split('_')
            user_id = int(user_id)
            if user_id in self.active_games:
                text, markup = self.create_question(user_id, difficulty)
                query.edit_message_text(text, reply_markup=markup)
                query.answer(f"Difficulty set to {difficulty.capitalize()}")
            return
        
        # Handle math answer
        _, target_user_id, answer = data.split('_')
        target_user_id = int(target_user_id)
        answer = int(answer)
        
        if target_user_id not in self.active_games:
            query.answer("Game expired. Start new with /math")
            return
        
        game = self.active_games[target_user_id]
        correct = (answer == game["answer"])
        time_taken = time.time() - game["start_time"]
        
        # Update stats
        stats = self.user_stats[target_user_id]
        stats["total"] += 1
        if correct:
            stats["correct"] += 1
            stats["streak"] += 1
            feedback = f"✅ Correct! ({time_taken:.1f}s)"
        else:
            stats["streak"] = 0
            feedback = f"❌ Wrong! Answer was {game['answer']}"
        
        # Generate new question
        new_text, new_markup = self.create_question(target_user_id)
        
        # Edit message with feedback and new question
        query.edit_message_text(
            text=f"{feedback}\n\n{new_text}",
            reply_markup=new_markup
        )
        
        # Update message ID in case it changed
        self.active_games[target_user_id]["message_id"] = query.message.message_id
        query.answer()

    def show_stats(self, update: Update, context: CallbackContext):
        """Handle /mathstats command"""
        user_id = update.effective_user.id
        if user_id in self.user_stats:
            stats = self.user_stats[user_id]
            accuracy = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            update.message.reply_text(
                f"📊 Math Game Stats:\n"
                f"Correct: {stats['correct']}/{stats['total']}\n"
                f"Accuracy: {accuracy:.1f}%\n"
                f"Current Streak: {stats['streak']}"
            )
        else:
            update.message.reply_text("Start playing with /math")

def add_math_handlers(dispatcher):
    game = MathGame()
    dispatcher.add_handler(CommandHandler("math", game.start_game))
    dispatcher.add_handler(CommandHandler("mathstats", game.show_stats))
    dispatcher.add_handler(CallbackQueryHandler(game.handle_answer, pattern="^(math|diff)_"))
    return game
