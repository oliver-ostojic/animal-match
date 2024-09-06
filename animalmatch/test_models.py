import pytest
from django.core.exceptions import ValidationError
from matcher.models import Quiz, Animal, QuizResult, User
from matcher.utils import fetch_animal_data_from_api


# test_models.py contains all the testcases for the classes in models.py


@pytest.mark.parametrize(
    "responses, expected_output", [
        ({"lifestyle": "?", "diet": "?", "location": "?", "group_behavior": "?"}, True),
        ({"lifestyle": "?", "diet": "?", "location": "?"}, False),
        ({"lifestyle": "?"}, False),
        ([1, 2, 3], False),
        ({""}, False),
        ([""], False),
        (20, False),
        (None, False)
    ]
)
@pytest.mark.quiz
def test_validate_response(responses, expected_output):
    if expected_output:
        assert Quiz.validate_response(responses)
    else:
        with pytest.raises(ValidationError):
            Quiz.validate_response(responses)


@pytest.fixture(autouse=True)
def animals_data():
    """
    Sample animal data from a Frog API call consisting of a list of dictionaries.
    """
    data = [
        {
            "name": "African Bullfrog",
            "taxonomy": {
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "class": "Amphibia",
                "order": "Anura",
                "family": "Pyxicephalidae",
                "genus": "Pyxicephalus",
                "scientific_name": "Pyxicephalus adspersus"
            },
            "locations": [
                "Africa"
            ],
            "characteristics": {
                "main_prey": "Reptiles, small mammals, small birds, insects, amphibians, including other frogs",
                "name_of_young": "Tadpole, polliwog, larva",
                "group_behavior": "Solitary",
                "estimated_population_size": "Unknown",
                "biggest_threat": "Habitat destruction, hunting, pet trade",
                "most_distinctive_feature": "Size",
                "other_name(s)": "Pixie frog, Giant African Bullfrog",
                "water_type": "Fresh",
                "litter_size": "As many as 4000 eggs laid at a time",
                "habitat": "Deserts, high veld, floodplains, grassland, savanna, farms, marshes, ponds, lakes",
                "predators": "Humans",
                "diet": "Carnivore",
                "type": "Amphibian",
                "common_name": "African bullfrog",
                "number_of_species": "1",
                "location": "Sub-Saharan Africa",
                "color": "YellowCreamOliveLight-Brown",
                "skin_type": "Permeable",
                "lifespan": "45 years",
                "weight": "0.9 to 18 kilograms (2 - 4 pounds)",
                "length": "11.43 - 25.4 centimeters (4.5 - 10 inches)",
                "age_of_sexual_maturity": "1.5 - 2 years"
            }
        },

        {
            "name": "African Clawed Frog",
            "taxonomy": {
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "class": "Amphibia",
                "order": "Anura",
                "family": "Pipidae",
                "genus": "Xenopus",
                "scientific_name": "Xenopus laevis"
            },
            "locations": [
                "Africa"
            ],
            "characteristics": {
                "prey": "Small Fish, Insects, Spiders",
                "name_of_young": "Tadpole",
                "group_behavior": "Solitary",
                "estimated_population_size": "Abundant",
                "biggest_threat": "Water pollution",
                "most_distinctive_feature": "Clawed front toes",
                "other_name(s)": "Platanna",
                "water_type": "Fresh",
                "incubation_period": "4 - 5 days",
                "age_of_independence": "5 days",
                "average_spawn_size": "2,000",
                "habitat": "Warm stagnant water with grassland",
                "predators": "Snakes, Birds, Small Mammals",
                "diet": "Carnivore",
                "lifestyle": "Nocturnal",
                "common_name": "African Clawed Frog",
                "number_of_species": "1",
                "location": "eastern and southern Africa",
                "slogan": "A particularly ferocious amphibian!",
                "group": "Amphibian",
                "color": "BrownGreyAlbino",
                "skin_type": "Permeable Scales",
                "top_speed": "5 mph",
                "lifespan": "8 - 15 years",
                "weight": "25g - 220g (1oz - 8oz)",
                "length": "2.5cm - 12cm (1in - 5in)",
                "age_of_sexual_maturity": "10 - 12 months"
            }
        },
        {
            "name": "Bullfrog",
            "taxonomy": {
                "kingdom": "Animalia",
                "phylum": "Chordata",
                "class": "Amphibia",
                "order": "Anura",
                "family": "Ranidae",
                "genus": "Lithobates",
                "scientific_name": "Lithobates catesbeianus"
            },
            "locations": [
                "Central-America",
                "North-America",
                "Ocean"
            ],
            "characteristics": {
                "main_prey": "Insects, Spiders, Small Fish",
                "distinctive_feature": "Powerful legs and cow-like call",
                "habitat": "Lakes, ponds, rivers and streams",
                "diet": "Carnivore",
                "lifestyle": "Solitary",
                "favorite_food": "Insects",
                "type": "Amphibian",
                "average_clutch_size": "20000",
                "slogan": "Has loud cow-like calls!",
                "color": "BrownGreyYellowBlackGreen",
                "skin_type": "Permeable",
                "top_speed": "10 mph",
                "lifespan": "6 - 10 years",
                "weight": "300g - 500g (10.5oz - 17.6oz)",
                "length": "9cm - 15cm (3.5in - 6in)"
            }
        }
    ]
    return data


@pytest.fixture
def quiz_with_animals():
    quiz = Quiz.objects.create(title="Frog")
    Animal.objects.create(name="Bullfrog",
                          habitat="Lake",
                          lifestyle="Solitary",
                          locations=["North-America", "South-America"],
                          diet="Carnivore",
                          lifespan="6 - 10 years",
                          image_url="https://example.com/image.jpg",
                          quiz=quiz,
                          species="Species"
                          )
    Animal.objects.create(name="Red Eyed Tree Frog",
                          habitat="Jungle",
                          lifestyle="Solitary",
                          locations=["South-America"],
                          diet="Carnivore",
                          lifespan="6 - 8 years",
                          image_url="https://example.com/image.jpg",
                          quiz=quiz,
                          species="Species"
                          )
    Animal.objects.create(name="Glass Frog",
                          habitat="Jungle",
                          group_behavior="Nocturnal",
                          locations=["Central-America"],
                          diet="Herbivore",
                          lifespan="6 - 8 years",
                          image_url="https://example.com/image.jpg",
                          quiz=quiz,
                          species="Species"
                          )
    return quiz


@pytest.mark.quizresult
@pytest.mark.django_db
def test_calculate_score_with_one_perfect_score(quiz_with_animals):
    # First create the QuizResult object to call calculate_score on
    responses = {"location": "Central-America", "diet": "Herbivore", "group_behavior": "Nocturnal"}
    result = QuizResult.objects.create(responses=responses,
                                       quiz=quiz_with_animals
                                       )
    # Call calculate_score
    result.calculate_score()
    # Assert that the result is as expected
    assert result.animal_match == "Glass Frog"
    assert result.score == 3


# Create separate test for animal_match with two same matches (don't assert
# that animal_match is as expected because its random

# Test with quiz that has no animals


@pytest.mark.parametrize(
    "test_quiz_id, responses, expected_output", [
        (0, {"lifestyle": "?", "diet": "?", "location": "?",
             "group_behavior": "?"}, True),  # Valid quiz_id and valid responses
        (1, {"lifestyle": "?", "diet": "?", "location": "?",
             "group_behavior": "?"}, False),  # Invalid quiz_id and valid responses
        (1, {""}, False),  # Invalid quiz_id and invalid responses
        (0, {""}, False),  # Valid quiz_id and invalid responses
        (None, {""}, False),  # Invalid response only
        (None, {"lifestyle": "?", "diet": "?", "location": "?", "group_behavior": "?"}, False),  # Valid responses only
        (0, None, False),  # Valid quiz_id
        (1, None, False),  # Invalid quiz_id
    ]
)
@pytest.mark.user
@pytest.mark.django_db
def test_take_quiz(mocker, test_quiz_id, responses, expected_output):
    # Patch result.calculate(). The focus is to test take_quiz()
    mocker.patch("matcher.models.QuizResult.calculate_score")
    # If valid output expected
    if expected_output:
        # Create quiz object
        quiz = Quiz.objects.create(title="Example")
        # Create result with take_quiz() using a valid quiz and responses
        result = User.take_quiz(quiz_id=quiz.id, responses=responses)
        # Assert that result is a QuizResult object type
        assert isinstance(result, QuizResult)
    # If invalid output expected (ValueError)
    else:
        # Use 'pytest.raises' to ensure that ValueError is raised
        with pytest.raises(ValueError):
            result = User.take_quiz(test_quiz_id, responses)


@pytest.fixture
def animal_data():
    return {"name": "Tree Frog", "taxonomy": {"scientific_name": "Scientific Name"},
            "locations": ["South-America"], "characteristics": {"habitat": "Swamp",
                                                                "diet": "Omnivore",
                                                                "group_behavior": "Solitary",
                                                                "lifespan": "10-12 years",
                                                                "lifestyle": "Nocturnal"
                                                                }}


@pytest.mark.parametrize(
    "deletions, expected_result, in_char", [
        ([], True, False),  # Test with animal data that has all attributes
        (["diet"], False, True),  # Test with animal data that is missing a diet
        (["habitat"], False, True),  # Test with animal data that is missing a habitat
        (["locations"], False, False),  # Test with animal data that is missing a locations
        (["group_behavior"], True, True),  # Test with animal data that is missing a group behavior
        (["lifestyle"], True, True),  # Test with animal data that is missing a lifestyle
        (["group_behavior", "lifestyle"], False, True),  # Test with animal data that is missing
        # both group behavior and lifestyle
        (["lifespan"], False, True),  # Test with animal that is missing lifespan
        (["scientific_name"], False, False) # Test with animal missing species name
    ]
)
@pytest.mark.animal
@pytest.mark.django_db
def test_validate_animal_data(deletions, expected_result, animal_data, in_char):
    # Check list of deletions and delete each item from dict
    # But first, check if item is inside characteristics dict
    if in_char:
        for item in deletions:
            animal_data["characteristics"].pop(item)
    else:
        for item in deletions:
            if item == "scientific_name":
                animal_data["taxonomy"].pop(item)
            else:
                del animal_data[item]
    # Pass animal_data to function
    validated = Animal.validate_animal_data(animal_data)
    # Assert that it is True or False
    assert validated == expected_result


@pytest.mark.quiz
def test_validate_quiz_with_not_enough_valid_animals(mocker):
    # Mock validate_animal_data for unit testing (isolation)
    mock_validate_animal_data = mocker.patch("matcher.models.Animal.validate_animal_data")
    # Set return value to True so all tests pass for testing
    mock_validate_animal_data.return_value = True
    # Set animal_data to have only one (valid) animal
    animal_data = [{"animal"}]
    # Call Quiz.validate_quiz()
    with pytest.raises(ValidationError) as exc_info:
        valid_animals, answers = Quiz.validate_quiz(animal_data)
    # Using exception details, check for correct message
    assert "Insufficient valid animals: unable to generate quiz." in str(exc_info.value)


@pytest.fixture
def six_valid_animals():
    animals = [
        {"characteristics": {"diet": "diff1,", "lifestyle": "same", "group_behavior": "same"}, "locations": ["same"]},
        {"characteristics": {"diet": "diff2,", "lifestyle": "same", "group_behavior": "same"}, "locations": ["same"]},
        {"characteristics": {"diet": "same,", "lifestyle": "same", "group_behavior": "same"}, "locations": ["diff1"]},
        {"characteristics": {"diet": "same,", "lifestyle": "diff2", "group_behavior": "same"}, "locations": ["diff2"]},
        {"characteristics": {"diet": "same,", "lifestyle": "same", "group_behavior": "diff1"}, "locations": ["same"]},
        {"characteristics": {"diet": "same,", "lifestyle": "same", "group_behavior": "diff2"}, "locations": ["same"]}
    ]
    return animals


@pytest.mark.parametrize(
    "attribute, error_message", [
        ("diet", "Not enough diets found: unable to generate quiz."),  # Unique diets insufficient
        ("locations", "Not enough locations found: unable to generate quiz."),  # Unique locations insufficient
        ("all", "None")  # Test that no validation errors are raised
    ]
)
@pytest.mark.quiz
def test_validate_quiz(mocker, attribute, error_message):
    # Mock validate_animal_data for unit testing (isolation)
    mock_validate_animal_data = mocker.patch("matcher.models.Animal.validate_animal_data")
    # Set return value to True so all tests pass for testing
    mock_validate_animal_data.return_value = True
    # Create animal_data with 2 animals with only one unique attribute
    # This is creating the animals that raises the specific attribute ValidationError
    animal_data = []
    for i in range(1, 7):
        # Create animal object with all unique attributes first
        animal = {"locations": ["a" * i], "characteristics": {
            "lifestyle": "a" * i,
            "diet": "a" * i,
            "group_behavior": "a" * i,
        }}
        if attribute == "diet":
            animal["characteristics"][attribute] = "a"
        elif attribute == "locations":
            animal[attribute] = "a"
        # Append the dictionary to the list now to simulate API data result
        animal_data.append(animal)
    # If expecting validation error
    if attribute == "diet" or attribute == "locations":
        # Call validate_quiz with animal_data
        with pytest.raises(ValidationError) as exc_info:
            valid_animals, answers = Quiz.validate_quiz(animal_data)
        # Assert that the error message is as expected
        assert error_message in str(exc_info.value)
    else:
        animals_in_quiz, answers = Quiz.validate_quiz(animal_data)
        assert animals_in_quiz == animal_data


@pytest.mark.quiz
def test_validate_quiz_with_enough_valid_animals(mocker):
    # Mock validate_animal_data for unit testing (isolation)
    mock_validate_animal_data = mocker.patch("matcher.models.Animal.validate_animal_data")
    # Set return value to True so all tests pass for testing
    mock_validate_animal_data.return_value = True
    # Create animal_data with 2 animals with only one unique attribute
    # This is creating the animals that raises the specific attribute ValidationError
    animal_data = []
    for i in range(6):
        # Create animal object with all unique attributes first
        animal = {"locations": ["a" * i], "characteristics": {
            "lifestyle": "a",
            "diet": "a" * i,
            "group_behavior": "a",
        }}
        # Append the dictionary to the list now to simulate API data result
        animal_data.append(animal)
    # Call validate_quiz with animal_data
    with pytest.raises(ValidationError) as exc_info:
        valid_animals, answers = Quiz.validate_quiz(animal_data)
    # Assert that the error message is as expected
    assert "Not enough lifestyles and group behaviors found: unable to generate quiz." in str(exc_info.value)


@pytest.fixture
def valid_animals():
    valid_animals = []
    for i in range(3):
        # Create animal object with all unique attributes first
        animal = {"name": "a" * i, "taxonomy": {"scientific_name": "a" * i}, "locations": ["a" * i],
                  "characteristics": {
                      "lifestyle": "a" * i,
                      "diet": "a" * i,
                      "lifespan": "a" * i,
                      "habitat": "a" * i
                  }}
        # Append the dictionary to the list now to simulate API data result
        valid_animals.append(animal)
    return valid_animals


@pytest.fixture
def answers():
    return {"diet": ['a', 'aa', 'aaa'], "location": ['a', 'aa', 'aaa'],
            "lifestyle": ['a', 'aa', 'aaa'], "group_behavior": []}


@pytest.mark.quiz
@pytest.mark.django_db
def test_validate_and_create_quiz_valid_quiz(mocker, valid_animals, answers):
    # Do all necessary patching for unit testing
    # Patch fetch_animal_data_from_api
    mock_fetch_animal_data_from_api = mocker.patch("matcher.models.fetch_animal_data_from_api")
    mock_fetch_animal_data_from_api.return_value = valid_animals
    # Patch validate_quiz
    mock_validate_quiz = mocker.patch("matcher.models.Quiz.validate_quiz")
    # Create the valid_animals to set as return value
    mock_validate_quiz.return_value = valid_animals, answers
    # Patch fetch_image_url_from_api
    mock_fetch_image_url_from_api = mocker.patch("matcher.models.fetch_image_url_from_api")
    mock_fetch_image_url_from_api.return_value = "url"
    # Call function to be tested
    quiz = Quiz.validate_and_create_quiz("Test animal search")
    # Assert that animals were all created
    assert quiz.animals.count() == 3
    # Assert that all questions were created
    assert quiz.questions.count() == 3
    # Assert that answers are correct
    for question in quiz.questions.all():
        assert question.answers.count() == 3


@pytest.mark.quiz
def test_validate_and_create_quiz_with_value_error(mocker):
    # Do all necessary patching for unit testing
    # Patch fetch_animal_data_from_api
    mock_fetch_animal_data_from_api = mocker.patch("matcher.models.fetch_animal_data_from_api")
    mock_fetch_animal_data_from_api.return_value = []
    # Call function to be tested
    with pytest.raises(ValueError) as exc_info:
        Quiz.validate_and_create_quiz("No results")
    assert "Animal search yielded no results: unable to generate quiz." in str(exc_info.value)


@pytest.mark.quiz
def test_validate_and_create_quiz_with_validation_error(mocker, valid_animals):
    # Do all necessary patching for unit testing
    # Patch fetch_animal_data_from_api
    mock_fetch_animal_data_from_api = mocker.patch("matcher.models.fetch_animal_data_from_api")
    mock_fetch_animal_data_from_api.return_value = valid_animals
    # Patch validate_quiz with validation error
    mock_validate_quiz = mocker.patch("matcher.models.Quiz.validate_quiz")
    mock_validate_quiz.side_effect = ValidationError("Some validation error")
    # Call function to be tested
    with pytest.raises(ValidationError) as exc_info:
        Quiz.validate_and_create_quiz("No results")
    assert "Some validation error" in str(exc_info.value)

