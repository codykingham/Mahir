# Mahir: Contextual Vocabulary Acquisition for Readers of Literature

> וְהֽוּא־סֹפֵ֤ר מָהִיר֙ בְּתֹורַ֣ת מֹשֶׁ֔ה

Mahir is a vocabulary acquisition app that focuses on regular, in-context exposure to lexical items within 
literary corpora. A number of vocabulary apps already exist which approach vocabulary acquisition in different
ways. For example, some solutions simply show a lexical item by itself, relying on algorithms to track
visited items and those due for review. Other methods employ a living-language approach, where terms are paired with 
images or sounds, thus providing invaluable cognitive context for remembering items. However, when the learning goal
is to acquire lexical items associated with a contrained literary corpus, unique challenges arise. Large 
corpora can contain many rare terms (*hapax legommena*) that make rote memorization difficult. Furthermore, terms 
in literary languages are best associated with the unique context where they appear. Yet doing simple reading alone
will require the reader to regularly consult a lexicon, slowing down the reading session and creating distraction.

Mahir addresses these concerns by presenting lexical items within the contexts where they appear,
while using learning algorithms to queue up items most-due for study. This method combines the unique benefits of 
simple reading with those of strategic, periodic review. The contexts provide the necessary associative data for 
learning rare terms; and the algorithm provides the regular exposure needed to recall items that would otherwise only 
be encountered rarely. Mahir also makes it possible to target particular parts of a corpus for review, preparing the 
user for productive, distraction-free reading sessions for select sections.

## Web App

Mahir is composed in Python using Django.

## Data Source

Data for the Hebrew Bible is extracted from the ETCBC's BHSA.
