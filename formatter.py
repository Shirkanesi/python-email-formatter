#!/usr/bin/python3
import re
import random

class LineFormatter:
    MAX_LINE_WIDTH: int = 42
    LINE_CLEANUP_THRESHOLD: int = MAX_LINE_WIDTH / 6

    NEWLINE_SEQUENCE_INPUT: str  = '\n'
    NEWLINE_SEQUENCE_OUTPUT: str = '\n'

    def __init__(self, max_line_width: int = MAX_LINE_WIDTH, line_cleanup_threshold: int = -1, newline_sequence_input: str = NEWLINE_SEQUENCE_INPUT, newline_sequence_output: str = NEWLINE_SEQUENCE_OUTPUT, move_links_to_bottom: bool = False):
        self.MAX_LINE_WIDTH = max_line_width
        if line_cleanup_threshold == -1:
            self.LINE_CLEANUP_THRESHOLD = self.MAX_LINE_WIDTH / 6
        else:
            self.LINE_CLEANUP_THRESHOLD = line_cleanup_threshold
        self.NEWLINE_SEQUENCE_INPUT = newline_sequence_input
        self.NEWLINE_SEQUENCE_OUTPUT = newline_sequence_output
        self.move_links_to_bottom: bool = move_links_to_bottom


    def find_split_index(self, line: str) -> int:
        if len(line) <= self.MAX_LINE_WIDTH:
            return len(line)

        i: int
        for i in range(self.MAX_LINE_WIDTH, int(self.MAX_LINE_WIDTH / 3), -1):
            if re.match('\s', line[i]):
                return i
        return self.MAX_LINE_WIDTH


    def cleanup_line(self, line: str) -> str:
        missing_chars: int = self.MAX_LINE_WIDTH - len(line)
        if missing_chars > self.LINE_CLEANUP_THRESHOLD:
            return line

        space_indices: list[int] = []
        for match in re.finditer('\s', line):
            space_indices.append(match.start())

        insert_indices: list[int] = []
        while len(insert_indices) < missing_chars and len(space_indices) > 0:
            insert_indices.extend(random.sample(space_indices, min(missing_chars - len(insert_indices), len(space_indices))))
        insert_indices.sort(reverse=True)

        index: int
        for index in insert_indices:
            line = line[0 : index] + " " + line[index : len(line)]

        return line


    def strip_wrongly_placed_newline(self, input: str) -> str:
        # TODO: use configured newline
        return re.sub(r'([^\.,\-\s\?])\s*\n\s*', r'\1 ', input) 

    
    def strip_links_to_bottom(self, input: str) -> str:
        if re.search('\[\s*\d\s*\]\s*(?:https?|s?ftp|dav|file):', input):
            return input
        else:
            output: str = ""
            links: list[str] = []
            i: int = 1
            last_pos: int = 0
            input = re.sub('(?:<a[^>]*href=.)?(?:mailto:)?(\S+@[^\s\,\-"><]+)(?:.*<\/a>)?', r'mailto://<\1>', input)
            for match in re.finditer('((?:https?|s?ftp|dav|file|mailto):\/\/\/?\S+)', input):
                output = output + input[last_pos : match.start()] + " [" + str(i) + "] "
                links.append(match.group(0))
                i = i + 1
                last_pos = match.end() + 1

            output = output + input[last_pos : len(input)]

            # Build list of links at bottom
            if len(links) > 0:
                output = output + self.NEWLINE_SEQUENCE_INPUT

                index: int
                link: str
                for index, link in enumerate(links):
                    output = output + "\n[" + str(index + 1) + "] " + link

            # cleanup messy whitespace around links
            output = re.sub('[^\S\r\n]+(\[\d\])[^\S\r\n]+', r' \1 ', output)
            output = re.sub('mailto:\/\/', r'', output)
            return output


    def format_string_to_width(self, original: str) -> str:
        output: list[str] = []
        processed: str = self.strip_wrongly_placed_newline(original)
        if self.move_links_to_bottom:
            processed = self.strip_links_to_bottom(processed)
        lines: list[str] = processed.split(self.NEWLINE_SEQUENCE_INPUT)

        line: str
        for line in lines:
            while True:
                line_length: int = len(line)
                if line_length == 0:
                    break
                split_index: int = self.find_split_index(line)
                new_part: str = line[0 : split_index]
                line: str = line[split_index + 1 : line_length]
                if line_length > self.MAX_LINE_WIDTH:
                    new_part = self.cleanup_line(new_part)
                output.append(new_part)
                if line_length <= self.MAX_LINE_WIDTH and line_length > self.MAX_LINE_WIDTH * 0.6:
                    output.append('\n')

        return self.NEWLINE_SEQUENCE_OUTPUT.join(output)


    def generate_headline(self) -> str:
        return "#" * self.MAX_LINE_WIDTH

