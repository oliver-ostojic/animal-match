import pytest
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import TestCase, Client
from django.urls import reverse
from matcher.models import Animal, Quiz, Question, QuizResult


class ResultsViewTests(TestCase):
    @pytest.mark.views
    @pytest.mark.django_db
    def test_results_view_animal_not_found(self):
        # Create client
        client = Client()
        # Generate the request
        response = client.get(reverse("matcher:results", kwargs={"animal_match": "Invalid name"}))
        # Assert that status code is correct
        assert response.status_code == 404
        # Assert that the proper template was used
        self.assertTemplateUsed(response, "matcher/error.html")

    @pytest.mark.views
    @pytest.mark.django_db
    def test_results_view_animal_found(self):
        # Create the animal we are mocking
        animal = Animal.objects.create(
            name="Tree Frog",
            habitat="Rainforest",
            lifestyle="Solitary",
            locations=["South-America"],
            diet="Herbivore",
            lifespan="10 years",
            image_url="https://example.com/image.jpg",
            quiz=Quiz.objects.create(title="Example Animal"),
            species="Species"
        )
        # Create client
        client = Client()
        # Call results_view
        response = client.get(reverse("matcher:results", kwargs={"animal_match": animal.name}))
        # Assert that status code is as expected
        assert response.status_code == 200
        # Assert that the proper template was used
        self.assertTemplateUsed(response, "matcher/results.html")
        # Assert animal is in response context
        assert response.context["animal"] == animal


# Test that the error_view is redirecting correctly for "Quiz not found"
# Send a quiz with a quiz_id that doesn't exist
@pytest.mark.views
@pytest.mark.django_db
def test_quiz_view_quiz_not_found(mocker):
    # Patch error_view
    mock_error_view = mocker.patch("matcher.views.error_view")
    mock_error_view.return_value = HttpResponse(status=404)
    # Set up the client
    client = Client()
    # Call results_view
    response = client.get(reverse("matcher:quiz", args=[0]))
    # Assert that status_code is correct
    assert response.status_code == 404
    args, kwargs = mock_error_view.call_args
    assert args[1] == "Quiz not found"


@pytest.fixture
def quiz_with_questions():
    # Create a quiz
    quiz = Quiz.objects.create(title="Frog")
    # Create a question for the quiz
    Question.objects.create(
        category="location",
        quiz=quiz
    )
    Question.objects.create(
        category="lifestyle",
        quiz=quiz
    )
    return quiz


@pytest.fixture
def result(quiz_with_questions):
    # Create a result
    result = QuizResult.objects.create(
        responses={},
        animal_match="Tree Frog",
        score=2,
        quiz=quiz_with_questions
    )
    return result


# Test that the results_view is redirecting correctly
# Send a quiz with a quiz_id that is valid and has a question to display and valid answer that passes validation
@pytest.mark.views
@pytest.mark.django_db
def test_quiz_view_valid_last_answer(mocker, quiz_with_questions, result):
    # Mock take_quiz()
    mock_take_quiz = mocker.patch("matcher.models.User.take_quiz")
    mock_take_quiz.return_value = result
    # Set up the client
    client = Client()
    # Call results_view
    response = client.post(reverse("matcher:quiz", args=[quiz_with_questions.id]),
                           data={
                               # Set question index to last question in order to load results_view
                               'question_index': 1,
                               'answer': 'some_answer'
                           })
    # Check for redirect status code
    assert response.status_code == 302
    # Assert the redirect URL is as expected
    expected_url = reverse("matcher:results", kwargs={"animal_match": result.animal_match})
    assert response.url == expected_url


# Test that quiz_view is rendered when a 'non-last' question is rendered
@pytest.mark.views
@pytest.mark.django_db
def test_quiz_view_valid_non_last_answer(quiz_with_questions, result):
    # Set up the client
    client = Client()
    # Call results_view
    response = client.post(reverse("matcher:quiz", args=[quiz_with_questions.id]),
                           data={
                               'answer': 'some_answer'
                           })
    # Check that status code is 'OK' successful quest
    assert response.status_code == 200
    # Check that proper URL was requested
    assert "matcher/quiz.html" in (t.name for t in response.templates)


# Test that the error_view is redirecting correctly for ValidationError
# Send a quiz with a quiz_id that is valid and has a question to display but an invalid answer
# that raises a ValidationError
@pytest.mark.views
@pytest.mark.django_db
def test_quiz_view_validation_error(mocker, result, quiz_with_questions):
    # Patch error_view
    mock_error_view = mocker.patch("matcher.views.error_view")
    mock_error_view.return_value = HttpResponse(status=400)
    # Mock take_quiz()
    mock_take_quiz = mocker.patch("matcher.models.User.take_quiz")
    mock_take_quiz.side_effect = ValidationError("invalid answer")
    # Set up the client
    client = Client()
    # Call results_view with a last question
    response = client.post(reverse("matcher:quiz", args=[quiz_with_questions.id]),
                           data={
                               # Set question index to last question in order to load results_view
                               'question_index': 1,
                               'answer': 'some_answer'
                           })
    # Check that the server was unable to process request
    assert response.status_code == 400
    # Check that the correct template was rendered
    args, kwargs = mock_error_view.call_args
    assert args[1].messages[0] == "invalid answer"


# Test that the error_view is redirecting correctly for ValueError
# Send a quiz with a quid_id that is valid and has a question to display but a ValueError is raised
@pytest.mark.views
@pytest.mark.django_db
def test_quiz_view_value_error(mocker, result, quiz_with_questions):
    # Patch error_view
    mock_error_view = mocker.patch("matcher.views.error_view")
    mock_error_view.return_value = HttpResponse(status=404)
    # Mock take_quiz()
    mock_take_quiz = mocker.patch("matcher.models.User.take_quiz")
    mock_take_quiz.side_effect = ValidationError("quiz not found")
    # Set up the client
    client = Client()
    # Call results_view with a last question
    response = client.post(reverse("matcher:quiz", args=[quiz_with_questions.id]),
                           data={
                               # Set question index to last question in order to load results_view
                               'question_index': 1,
                               'answer': 'some_answer'
                           })
    # Check that the server was unable to process request
    assert response.status_code == 404
    # Check that the correct template was rendered
    args, kwargs = mock_error_view.call_args
    assert args[1].messages[0] == "quiz not found"


# Test that the error_view is redirecting correctly for "No answer selected"
# Send a quiz where no answer is selected
@pytest.mark.views
@pytest.mark.django_db
def test_quiz_view_answer_not_found(mocker, result, quiz_with_questions):
    # Patch error_view
    mock_error_view = mocker.patch("matcher.views.error_view")
    mock_error_view.return_value = HttpResponse(status=400)
    # Set up the client
    client = Client()
    # Call results_view with a last question
    response = client.post(reverse("matcher:quiz", args=[quiz_with_questions.id]))
    # Check that the server was unable to process request
    assert response.status_code == 400
    # Check that the correct template was rendered
    args, kwargs = mock_error_view.call_args
    assert args[1] == "No answer selected"


# Test that "matcher/quiz.html" is rendered correctly
# Send a quiz with request with no Post method
@pytest.mark.views
@pytest.mark.django_db
def test_quiz_view_no_post_method(result, quiz_with_questions):
    # Call client
    client = Client()
    # Call quiz_view
    response = client.get(reverse("matcher:quiz", args=[quiz_with_questions.id]))
    # Check that the correct error is called
    assert response.status_code == 200
    # Check that the correct template was rendered
    assert "matcher/quiz.html" in [t.name for t in response.templates]
    # Check that the render context is correct
    assert response.context["quiz"] == quiz_with_questions
    assert response.context["question"] == quiz_with_questions.questions.all()[0]
    assert response.context["question_index"] == 0


@pytest.mark.views
def test_home_view_get_method():
    # Create client first
    client = Client()
    # Create request with get method
    response = client.get(reverse("matcher:home"))
    # Check for OK status code
    assert response.status_code == 200
    # Check for the correct template
    assert "matcher/home.html" in [t.name for t in response.templates]


@pytest.mark.views
def test_home_view_post_no_quiz_search():
    # Create client first
    client = Client()
    # Create request with get method
    response = client.post(reverse("matcher:home"))
    # Retrieve all messages
    messages = list(get_messages(response.wsgi_request))
    # Check that only one message exists
    assert len(messages) == 1
    # Check that the error message level is 40 for ERROR
    assert messages[0].level == 40
    # Check that the message is correct
    assert str(messages[0].message) == "Please enter an animal name."
    # Check that the correct template is rendered
    assert "matcher/home.html" in [t.name for t in response.templates]


@pytest.mark.parametrize(
    "does_quiz_search_exist", [True, False]
)
@pytest.mark.views
@pytest.mark.django_db
def test_home_view_with_post_that_redirects_to_quiz_view(does_quiz_search_exist, mocker):
    if does_quiz_search_exist:
        # Create a quiz, so that the search already exists
        quiz = Quiz.objects.create(title="Animal that exists")
    else:
        # Quiz does not exist, so we will mock validate_and_create_quiz to make one
        mock_validate_and_create_quiz = mocker.patch("matcher.models.Quiz.validate_and_create_quiz")
        # Create return value
        quiz = Quiz.objects.create(title="Animal that exists")
        mock_validate_and_create_quiz.return_value = quiz
    # Create client
    client = Client()
    # Create request with get method
    response = client.post(reverse("matcher:home"), data={'title': 'Animal that exists'})
    # Check that the redirect code is correct
    assert response.status_code == 302
    # Check that the url redirect is correct
    assert response.url == reverse("matcher:quiz", kwargs={'quiz_id': quiz.id})


@pytest.mark.parametrize(
    "error, message", [
        ("Validation", "Some validation error"),
        ("Value", "Some value error")
    ]
)
@pytest.mark.views
@pytest.mark.django_db
def test_home_view_with_value_or_validation_errors(mocker, error, message):
    # Mock validation and creation process of quiz
    mock_validate_and_create_quiz = mocker.patch("matcher.models.Quiz.validate_and_create_quiz")
    # Set return values
    if error == "Validation":
        mock_validate_and_create_quiz.side_effect = ValidationError(message)
    elif error == "Value":
        mock_validate_and_create_quiz.side_effect = ValueError(message)
    # Create client
    client = Client()
    # Create request with get method
    response = client.post(reverse("matcher:home"), data={'title': 'Some animal'})
    # Retrieve all messages
    messages = list(get_messages(response.wsgi_request))
    # Check that only one message exists
    assert len(messages) == 1
    # Check that the error message level is 40 for ERROR
    assert messages[0].level == 40
    # Check that the message is correct
    assert messages[0].message == message
    # Check that the correct template is rendered
    assert "matcher/home.html" in [t.name for t in response.templates]


@pytest.mark.views
def test_error_view_with_default_values():
    # Setup client
    client = Client()
    # Call error_view with no 'e' or 'status_code'
    response = client.get(reverse("matcher:error"))
    assert "matcher/error.html" in [t.name for t in response.templates]
    # Check that the template was rendered OK
    assert response.status_code == 200
    # Check that context has default values
    assert response.context["status_code"] == 404
    assert response.context["error"] == "An unknown error occurred."


@pytest.mark.views
def test_error_view_with_input_values():
    # Setup client
    client = Client()
    # Call error_view with 'e' and 'status_code'
    response = client.get(reverse("matcher:error", kwargs={"status_code": 400, "e": "Some error"}))
    assert "matcher/error.html" in [t.name for t in response.templates]
    # Check that the template was rendered OK
    assert response.status_code == 400
    # Check that context has default values
    assert response.context["status_code"] == 400
    assert response.context["error"] == "Some error"
