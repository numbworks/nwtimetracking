% nwtime

# NAME
nwtime - runs automated data analysis tasks on a time tracking file

# SYNOPSIS
**nwtime** [command] [options]

# DESCRIPTION
**nwtime** is a CLI application that can run several automated data analysis tasks on a time tracking file and save the results as a PDF report. It’s designed to facilitate and gamify a continuous learning journey.

# COMMANDS

**save**
Runs all the data analysis tasks against the time tracking file and saves the outcome as PDF report.

# OPTIONS

**--input_path**
The path to the time tracking file in Excel format.

**--nrows**
Latest row number to process in the time tracking file.

*--folder_path*
The path to the folder into which the PDF report will be saved. Default: current folder.

*--help, -h*
Shows help and usage information.

# EXAMPLES

**Run it against a time tracking file:**

```text
nwtime \
	--input_path "/data/Time Tracking.xlsx" \
	--nrow 371 
```

**Run it against a time tracking file with custom `folder_path`:**

```text
nwtime \
	--input_path "/data/Time Tracking.xlsx" \
	--nrow 371 \
	--folder_path "/home/nwtimetracking/"
```

# AUTHOR
numbworks (numbworks@gmail.com)