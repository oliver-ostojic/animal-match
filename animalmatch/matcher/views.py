from django.contrib import messages
from django.shortcuts import render, redirect
from matcher.models import Animal, Quiz, User
from django.core.exceptions import ValidationError


def error_view(request, e=None, status_code=None):
    """
    Display error page and respective error code and error message
    """
    return render(request, "matcher/error.html",
                  {"error": str(e) if e else "An unknown error occurred.",
                   "status_code": status_code if status_code else 404},
                  status=status_code)


def home_view(request):
    """
    This view is the home page where a user can begin their initial animal search
    for a quiz
    """
    # First get the 6 most popular animal quizzes, split into two lists for display
    top_three = []
    top_four_to_six = []
    if Quiz.objects.all().count() >= 3:
        i = 1
        while i <= 3:
            quiz = Quiz.retrieve_quiz_by_popularity_rank(i)
            top_three.append(quiz)
            i += 1
    if Quiz.objects.all().count() >= 6:
        i = 4
        while i <= 6:
            quiz = Quiz.retrieve_quiz_by_popularity_rank(i)
            top_four_to_six.append(quiz)
            i += 1
    # Upload main home view
    if request.method == 'GET':
        return render(request, "matcher/home.html", context={"top_three": top_three,
                                                             "top_four_to_six": top_four_to_six})
    # If a search to generate a quiz is made:
    if request.method == 'POST':
        title = request.POST.get('title')
        # If the 'title' search POSTed exists
        if title:
            # If we can get the animal quiz, and it exists, redirect to quiz_view
            try:
                quiz = Quiz.objects.get(title=title.title())
                # Redirect to quiz_view
                return redirect("matcher:quiz", quiz_id=quiz.id)
            except Quiz.DoesNotExist:
                # Else, Verify animal can create a quiz
                try:
                    quiz = Quiz.validate_and_create_quiz(title)
                    # If verified, redirect to quiz_view
                    return redirect("matcher:quiz", quiz_id=quiz.id)
                except ValidationError as e:
                    # Had to pass in 'e' this way because of list wrapping found in unit testing
                    messages.error(request, ', '.join(e.messages))
                    # Redirect to error page
                    return render(request, "matcher/home.html", context={"top_three": top_three,
                                                                         "top_four_to_six": top_four_to_six})
                # If ValueError is raised, redirect to error page
                except ValueError as e:
                    messages.error(request, str(e))
                    return render(request, "matcher/home.html", context={"top_three": top_three,
                                                                         "top_four_to_six": top_four_to_six})
        else:
            messages.error(request, "Please enter an animal name.")
            return render(request, "matcher/home.html", context={"top_three": top_three,
                                                                 "top_four_to_six": top_four_to_six})


def results_view(request, animal_match):
    """
    This view displays the results of a user's quiz attempt. It displays the resulting
    animal's data and image
    """
    # Attempt to get the animal match
    try:
        animal = Animal.objects.get(name=animal_match)
    # If the animal could not be found, display an error page
    except Animal.DoesNotExist:
        return error_view(request, "Animal not found", status_code=404)
    # Return HttpResponseRedirect to redirect page to results.html
    return render(request, "matcher/results.html", {"animal": animal})


def quiz_view(request, quiz_id):
    """
    This view displays each quiz question one at a time, and manages the state of the
    quiz. When a user answers a question and clicks 'Next', the view will validate the
    answer, store it, and fetch the next question to display. If the last question
    is displayed, a 'Submit' button should redirect the user to results_view().
    """
    # Get the quiz from quiz_id
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    # If quiz does not exist, display error page
    except Quiz.DoesNotExist:
        return error_view(request, "Quiz not found", 404)
    # Get the current question index (used to track current question)
    # or return zero to start with first question
    curr_question_index = int(request.POST.get('question_index', 0))
    # Handle POST request for an answer submission
    if request.method == "POST":
        # Try to get the answer_id if it exists from
        selected_answer = request.POST.get('answer')
        # Store the answer if it exists
        if selected_answer:
            # Get the category of the current question
            curr_question = quiz.questions.all()[curr_question_index]
            question_category = curr_question.category
            # Get the responses, and return an empty dict, if it's the first
            responses = request.session.get('quiz_responses', {})
            # Add the answer to the responses
            responses[question_category] = selected_answer
            # Add the responses to the session
            request.session['quiz_responses'] = responses
            # Check to see if this is the last question
            if curr_question_index + 1 >= quiz.questions.count():
                # Try processing the quiz take_quiz()
                try:
                    result = User.take_quiz(quiz_id, responses)
                    # Redirect to the result page
                    return redirect("matcher:results", animal_match=result.animal_match)
                # If there is a validation error, return an error page
                except ValidationError as e:
                    return error_view(request, e, 400)
                # If there is a value error, return an error page
                except ValueError as e:
                    return error_view(request, e, 404)
            # If this is not the last question, move to the next question
            else:
                print(curr_question_index)
                curr_question_index += 1
                print(curr_question_index)
        # Else, return HttpResponse that no answer was selected
        else:
            return error_view(request, "No answer selected", 400)
    # Get the list of questions
    questions = quiz.questions.all()
    # Get the next question and return it
    curr_question = questions[curr_question_index]
    curr_answers = questions[curr_question_index].answers.all()
    print(request.POST)
    print(curr_question_index)
    return render(request, "matcher/quiz.html", {
        "quiz": quiz,
        "question": curr_question,
        "question_index": curr_question_index,
        "answers": curr_answers
    })
