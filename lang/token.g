(?P<COMMENT>//[^\n]*)                                     # single-line comment
| (?P<IDENTIFIER>[A-Za-z_]\w*)                            # identifiers and keywords
| (?P<FLOAT>\d+\.\d+)                                     # float numbers
| (?P<INTEGER>\d+)                                        # integer numbers
| (?P<STRING>"(?:\\.|[^"\\])*")                           # double-quoted strings with escape support
| (?P<OPERATOR>\+=|-=|\*=|/=|%=|==|<=|>=|!=|&&|\|\||=|\+|\-|\*|\/|%|<|>|\(|\)|\{|\}|;|,)  # operators and punctuation
| (?P<DOT_OPERATOR>\.)                                    # dot operator (for object properties/methods)
| (?P<NEWLINE>\n)                                         # new line
