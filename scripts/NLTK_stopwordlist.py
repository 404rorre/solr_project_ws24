import os
import nltk
from nltk.corpus import stopwords

# Download the stopwords
nltk.download('stopwords')

# Get the stopword list for English
stop_words = set(stopwords.words('english'))

# Sort the stopword list for better readability
sorted_stop_words = sorted(stop_words)

# Specify the file path
#file_path = r"schema_files/base_DFI/conf/lang\stopwords_en.txt"
file_path = os.path.join("external_schema_files","stopwords_en.txt")

# Write the stopword list to the file
with open(file_path, 'w') as file:
    file.write('\n'.join(sorted_stop_words))

print(f"Stopword list saved at: {file_path}")

