
import re

def is_likely_poem(content):
    if not content:
        return False
    
    lines = content.strip().split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    if not non_empty_lines:
        return False
        
    avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
    short_lines_ratio = sum(1 for line in non_empty_lines if len(line) < 50) / len(non_empty_lines)

    # Heuristics for poem detection:
    # 1. Short average line length (poems usually have shorter lines).
    # 2. High ratio of short lines.
    # 3. Presence of stanza breaks (double newlines) is common but prose also has paragraphs.
    # 4. Hindi/Urdu words often appear in poems in this specific corpus (relying on user context).
    # 5. Keywords often found in poem titles or content here (e.g., "Ghazal", "Poem", "kabhi").
    
    # Check for prose markers
    if avg_line_length > 60: # Prose usually has longer lines filling the width
        return False
        
    if short_lines_ratio < 0.6: # If mostly long lines, likely prose
        return False

    return True

input_file = "journal_entries_compiled.md"
output_file = "journal_poems_only.md"

with open(input_file, "r") as f:
    content = f.read()

# Split by the separator used in compilation
entries = content.split("---")

poem_entries = []

# preserve header
header = entries[0]
entries = entries[1:]

for entry in entries:
    entry_stripped = entry.strip()
    if not entry_stripped:
        continue
    
    # Split header and body
    # Assuming standard format: ## Title \n **Date:** ... \n \n Body
    parts = entry_stripped.split('\n', 3)
    
    if len(parts) >= 3:
        body = parts[-1]
        
        # Specific overrides based on known content from view_file
        title_line = parts[0]
        
        # Explicitly identified poems based on visual inspection of the user's file
        is_poem = is_likely_poem(body)
        
        # Manual overrides for mixed or tricky cases seen in the file
        lower_body = body.lower()
        if "quiz" in lower_body or "test" in lower_body or "results:" in lower_body: 
            is_poem = False # Survey/Quiz results
        if "update" in title_line.lower() or "chit-chat" in title_line.lower():
            is_poem = False
            
        # Specific titles that looked like poems in the file view:
        poem_titles = [
            "Kuch log kabhi kuch", "kabhi yun hua ke", "Morning 'O' Morning",
            "Kyon hai yeh shak-o-shuba", "yet another from my collection",
            "something more", "Kuch baaton ke hi chaakar mein", "miss hope tum ho tope",
            "Soch", "Naari ka abhimaan sahi hai", "For all we are", "Changing Times",
            "Hum Matwale Hain", "The Time flies by", "badhai sandesh", "Untitled",
            "Q&A", "Random Poem", "and the story continues", "Maafi",
            "Kyun main itni baat karta hun", "Khushi hai aaj ya", "Vicchoh",
            "Matrix Desi Istyle mein", "Naya Warsh", "Ghazal writing",
            "Kya hai yah sab", "Subah hai aati", "Naari"
        ]
        
        if any(pt.lower() in title_line.lower() for pt in poem_titles):
            is_poem = True
            
        # Specific overrides for prose
        prose_titles = [
            "Generic Chit-Chat", "Nothing New", "How Torturous a movie can be",
            "koi mujhe kaam do", "Oh God Why do I need to say it", 
            "A Journey into the Wild", "Re-login", "For what do we exist",
            "Whats latest", "Living alone", "Calvin", "Random Thoughts", 
            "Nourtourn 2005", "Working with multiple windows", "Supra Maan",
            "Forward Menace", "birthdate"
        ]

        if any(pt.lower() in title_line.lower() for pt in prose_titles):
            is_poem = False

        if is_poem:
            poem_entries.append(entry)

with open(output_file, "w") as f:
    f.write("# Collected Poems\n\nDerived from Journal Entries\n\n")
    f.write("---\n".join(poem_entries))

print(f"Filtered {len(poem_entries)} poems out of {len(entries)+1} entries.")
