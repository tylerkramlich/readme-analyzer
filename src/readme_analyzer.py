from salesforce_api import Salesforce
import configparser

class ReadmeAnalyzer:
    def __init__(self, config_path):
        self.config_path = config_path
        self.DOCUMENT_HEADERS = []
        self.README_PATH = 'src/README.md'

        self.__initialize_config_file()
        self.__initialize_readme()
        self.__initialize_sf_client()
        self.__initialize_document_headers()
        self.__initialize_tokens()

    def __initialize_config_file(self):
        self.config = configparser.RawConfigParser()
        self.config.read(self.config_path)

    def __initialize_readme(self):
        self.README = open(self.README_PATH, 'r')

    def __initialize_sf_client(self):
        username = self.config.get('AUTH', 'USERNAME')
        password = self.config.get('AUTH', 'PASSWORD')
        security_token = self.config.get('AUTH', 'SECURITY_TOKEN')

        self.client = Salesforce(username=username,
            password=password,
            security_token=security_token)

    def __initialize_document_headers(self):
        self.DOCUMENT_HEADERS = str.split(self.config.get('HEADERS', 'DOCUMENT_HEADERS'), ',')

    def __initialize_markdown_tags(self):
        pass

    def __initialize_tokens(self):
        self.APEX_EXAMPLE_START_TAG = self.config.get('TOKENS', 'APEX_EXAMPLE_START_TAG')
        self.APEX_EXAMPLE_END_TAG = self.config.get('TOKENS','APEX_EXAMPLE_END_TAG')
        self.TABLE_COLUMN = self.config.get('TOKENS', 'TABLE_COLUMN')

    def __apex_script_executor(self, apex_code):
        execution_result = self.client.tooling.execute_apex(apex_code)
        if (execution_result.success == True):
            print('Apex Executed Successfully.')
        else:
            print(execution_result.compile_problem)

    def __examine_found_tokenlist_for_errors(self, tokenList, lineNum):
        for pos in range(0, len(tokenList)-1):
            if tokenList[pos] == '<column>':
                if tokenList[pos+1] != '<whitespace>':
                    print('Error at', lineNum) # TODO: More descriptive error based on parser
            if tokenList[pos] == '<identifier>':
                if tokenList[pos+1] == '<column>':
                    print('Error at', lineNum)

    def __identifiy_tokens_in_table_row(self, line):
        tokenList = []
        identifier = ''
        pos = 0
        for pos in range(0, len(line)):
            if line[pos].isalnum():
                identifier += line[pos]
                peek = line[pos+1]
                if (peek.isalnum() == False):
                    tokenList.append('<identifier>')
            if line[pos] == '|':
                tokenList.append('<column>')
            if line[pos] == ' ':
                tokenList.append('<whitespace>')

        return tokenList

    def check_section_order(self, README):
        print('Executing check section order...')

        currentHeaderIndex = 0
        next(README) # Skips header line
        for line in README:
            if line[0] == '#':
                line = line.strip('\n')
                if line != self.DOCUMENT_HEADERS[currentHeaderIndex]: # TODO: Raise exceptions properly
                    print('DANGER. DANGER.', self.DOCUMENT_HEADERS[currentHeaderIndex], 'OUT OF PLACE')
                currentHeaderIndex = currentHeaderIndex + 1

        print('Executed check section order.')

    def apex_script_finder(self):
        print('Executing Apex script finder...')

        CODE_FLAG = False
        APEX_SCRIPT_CODE = ''
        for line in self.README:
            line = line.strip('\n')
            if line == self.APEX_EXAMPLE_END_TAG:
                CODE_FLAG = False
                self.__apex_script_executor(APEX_SCRIPT_CODE) # TODO: Raise apex execution error properly
                APEX_SCRIPT_CODE = ''

            if CODE_FLAG == True:
                APEX_SCRIPT_CODE += line

            if line == self.APEX_EXAMPLE_START_TAG:
                CODE_FLAG = True

        print('Executed Apex script finder.')

    def scan_for_tables(self):
        print('Executing Scan for Tables...')

        line_num = 1
        for line in self.README:
            if line[0] == self.TABLE_COLUMN:
                tokenList = self.__identifiy_tokens_in_table_row(line)
                self.__examine_found_tokenlist_for_errors(tokenList, line_num)
            line_num += 1

        print('Executed Scan for Tables')

    def runAll(self):
        print('Executing all components...')

        self.check_section_order(self.README)
        self.apex_script_finder()
        self.scan_for_tables()

        # TODO: Bubble up all output to a single file

        print('Finished.')