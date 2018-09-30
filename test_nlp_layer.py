from nlp_layer import NLP


class TestNLP:
    def __init__(self):
        self.nlp = NLP()

    def test_parse_input_play(self):
        output = self.nlp.parse_input('play the clash')
        assert (str(output[0]) == "['control_play']")
        assert (str(output[1]) == "clash")

    def test_parse_input_query(self):
        output = self.nlp.parse_input('Who is this artist')
        assert (str(output[0]) == "['query_artist']")
        assert (str(output[1]) == '')

    def test_parse_input_kbapi(self):
        # TODO: This test relies on a hardcoded value in the API,
        #       so it will need to be updated once that is implemented.
        output = self.nlp.parse_input('play the who')
        assert (str(output[0]) == "['control_play']")
        assert (str(output[1]) == 'The Who')

    def run_tests(self):
        print("Running tests...")
        self.test_parse_input_play()
        self.test_parse_input_query()
        self.test_parse_input_kbapi()
        print("Finished!")


if __name__ == '__main__':
    TestNLP().run_tests()
