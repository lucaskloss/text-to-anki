import genanki


# Define a custom note model for vocabulary cards
VOCAB_MODEL = genanki.Model(
    1607392319,  # Unique model ID
    'German Vocabulary Model',
    fields=[
        {'name': 'German'},
        {'name': 'English'},
        {'name': 'Example'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '<div style="font-size: 24px; text-align: center;">{{German}}</div>',
            'afmt': '''
                <div style="font-size: 24px; text-align: center;">{{German}}</div>
                <hr id="answer">
                <div style="font-size: 18px; margin-top: 20px;">{{English}}</div>
                {{#Example}}
                <hr>
                <div style="font-size: 14px; color: #666; margin-top: 15px;">
                    <strong>Example:</strong><br>
                    {{Example}}
                </div>
                {{/Example}}
            ''',
        },
    ],
    css='''
        .card {
            font-family: arial;
            color: black;
            text-align: center;
            padding: 20px;
        }
        
        hr {
            border: none;
            border-top: 1px solid #ccc;
            margin: 20px 0;
        }
    '''
)


def create_note_model():
    """Returns the vocabulary note model."""
    return VOCAB_MODEL
