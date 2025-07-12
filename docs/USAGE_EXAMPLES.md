# 💡 Usage Examples

Comprehensive examples showing how to use the Browser Agent for various tasks.

## Basic Web Interactions

### Simple Navigation and Search

```bash
uv run main.py run --task "Navigate to google.com and search for 'Python tutorials'"
```

**What the agent does:**

1. Opens browser and navigates to google.com
2. Finds the search box
3. Types "Python tutorials"
4. Clicks search or presses Enter
5. Reports the search results

### Form Filling

```bash
uv run main.py run --task "Go to httpbin.org/forms/post, fill out the contact form with test data, and submit it"
```

**Agent workflow:**

1. Navigates to the form page
2. Analyzes form fields
3. Fills each field with appropriate test data
4. Submits the form
5. Confirms submission success

## E-commerce and Shopping

### Product Research

```bash
uv run main.py run --task "Search Amazon for 'wireless headphones under $100', sort by customer rating, and show me the top 3 options with prices and ratings"
```

**Complex workflow:**

1. Navigates to Amazon
2. Searches for wireless headphones
3. Applies price filter (under $100)
4. Sorts by customer rating
5. Extracts top 3 results with details
6. Formats and presents the information

### Price Comparison

```bash
uv run main.py run --task "Compare the price of iPhone 15 on Apple.com, Amazon, and Best Buy, and tell me which has the best deal"
```

**Multi-site comparison:**

1. Visits Apple.com and finds iPhone 15 price
2. Searches Amazon for the same model
3. Checks Best Buy for pricing
4. Compares all prices and highlights the best deal

## Information Gathering

### News Aggregation

```bash
uv run main.py run --task "Visit BBC News, CNN, and Reuters, find the top technology news story from each, and summarize the main points"
```

**News research workflow:**

1. Visits each news site sequentially
2. Identifies technology sections
3. Finds top stories in each
4. Extracts key information
5. Creates a consolidated summary

### Research Tasks

```bash
uv run main.py run --task "Research the latest developments in renewable energy on Wikipedia, find 3 recent breakthrough technologies, and explain how they work"
```

**Research methodology:**

1. Navigates to Wikipedia
2. Searches for renewable energy topics
3. Identifies recent developments
4. Extracts technical details
5. Explains each technology clearly

## Social Media and Communication

### Social Media Monitoring

```bash
uv run main.py run --task "Check the latest posts on Hacker News, find discussions about AI, and summarize the main opinions and trends"
```

**Social analysis:**

1. Navigates to Hacker News
2. Scans recent posts for AI-related content
3. Reads comments and discussions
4. Identifies common themes and opinions
5. Summarizes trends and insights

### Content Creation

```bash
uv run main.py run --task "Based on the trending topics on Twitter today, suggest 5 blog post ideas for a tech blog"
```

**Content ideation:**

1. Visits Twitter trending topics
2. Identifies technology-related trends
3. Analyzes engagement and discussion
4. Generates relevant blog post ideas
5. Provides brief outlines for each

## Professional and Business Tasks

### Job Search

```bash
uv run main.py run --task "Search for Python developer jobs in San Francisco on LinkedIn, filter for remote-friendly positions, and show me the top 5 matches with salary information"
```

**Job search automation:**

1. Navigates to LinkedIn Jobs
2. Sets up search criteria
3. Applies location and remote filters
4. Sorts by relevance or date
5. Extracts job details and salary info

### Market Research

```bash
uv run main.py run --task "Research competitors of Shopify by visiting their websites, comparing their pricing plans, and creating a feature comparison"
```

**Competitive analysis:**

1. Identifies Shopify competitors
2. Visits each competitor's website
3. Finds pricing information
4. Compares features and capabilities
5. Creates structured comparison

## Educational and Learning

### Course Discovery

```bash
uv run main.py run --task "Find the best online machine learning courses on Coursera and edX, compare their ratings, duration, and prerequisites"
```

**Educational research:**

1. Searches both platforms for ML courses
2. Extracts course details and ratings
3. Compares duration and requirements
4. Ranks courses by various criteria
5. Provides recommendations

### Tutorial Following

```bash
uv run main.py run --task "Follow the first 3 steps of the Python tutorial on python.org and report what you learned"
```

**Interactive learning:**

1. Navigates to Python tutorial
2. Reads and follows instructions
3. Reports on each step's content
4. Summarizes key learning points

## Entertainment and Lifestyle

### Event Planning

```bash
uv run main.py run --task "Find upcoming concerts in Los Angeles this weekend, check the weather forecast, and recommend the best outdoor venue considering the weather"
```

**Event planning workflow:**

1. Searches for concerts in LA
2. Filters by weekend dates
3. Checks weather forecast
4. Identifies outdoor venues
5. Makes weather-based recommendations

### Travel Research

```bash
uv run main.py run --task "Research flights from New York to London for next month, find the cheapest options, and check hotel prices near popular attractions"
```

**Travel planning:**

1. Searches flight comparison sites
2. Finds best price options
3. Researches London attractions
4. Searches for nearby hotels
5. Compares accommodation prices

## Technical and Development

### Documentation Research

```bash
uv run main.py run --task "Look up the latest features in React 18 from the official documentation, and explain the most important changes for developers"
```

**Technical research:**

1. Navigates to React documentation
2. Finds React 18 specific content
3. Identifies new features
4. Explains technical implications
5. Prioritizes by developer impact

### API Exploration

```bash
uv run main.py run --task "Explore the GitHub API documentation, find how to create a repository via API, and show me the required parameters"
```

**API documentation review:**

1. Navigates to GitHub API docs
2. Searches for repository creation
3. Extracts API endpoint details
4. Lists required parameters
5. Provides usage examples

## Data Collection and Analysis

### Survey Creation

```bash
uv run main.py run --task "Visit SurveyMonkey, explore their survey templates for customer satisfaction, and describe the key questions they recommend"
```

**Template analysis:**

1. Explores SurveyMonkey templates
2. Focuses on customer satisfaction
3. Analyzes question types
4. Identifies best practices
5. Summarizes recommendations

### Trend Analysis

```bash
uv run main.py run --task "Check Google Trends for 'cryptocurrency' vs 'blockchain' over the past year and explain the trend patterns"
```

**Trend research:**

1. Navigates to Google Trends
2. Sets up comparison search
3. Analyzes yearly data
4. Identifies patterns and peaks
5. Explains potential causes

## Interactive Examples with User Input

### Personalized Shopping

```bash
uv run main.py run --task "Help me find a laptop for graphic design work. Ask me about my budget, preferred screen size, and software requirements, then search and recommend options"
```

**Interactive consultation:**

1. Asks user about budget preferences
2. Inquires about screen size needs
3. Determines software requirements
4. Searches based on criteria
5. Provides personalized recommendations

### Custom Research

```bash
uv run main.py run --task "I want to learn about a specific technology topic. Ask me what I'm interested in, then find the best learning resources and create a study plan"
```

**Adaptive learning:**

1. Asks about technology interests
2. Inquires about current skill level
3. Determines learning preferences
4. Searches for appropriate resources
5. Creates customized study plan

## Advanced Multi-Step Workflows

### Complete Website Analysis

```bash
uv run main.py run --task "Analyze a competitor's website: check their homepage, pricing page, and about page. Extract their value proposition, pricing strategy, and team information. Then compare it to our website."
```

**Comprehensive analysis:**

1. Navigates through multiple pages
2. Extracts structured information
3. Analyzes value propositions
4. Compares pricing strategies
5. Provides competitive insights

### Email Campaign Research

```bash
uv run main.py run --task "Research email marketing best practices by visiting Mailchimp, Constant Contact, and HubSpot. Find their recommended subject line strategies and compile a best practices guide"
```

**Multi-source research:**

1. Visits multiple marketing platforms
2. Searches for best practice content
3. Extracts subject line strategies
4. Compiles unified guidelines
5. Creates actionable recommendations

## Tips for Writing Effective Tasks

### Be Specific About Goals

```bash
# Good
"Find the 3 highest-rated Italian restaurants in downtown Seattle with outdoor seating"

# Too vague
"Find some restaurants"
```

### Include Context and Constraints

```bash
# Good
"Search for Python web development jobs that are fully remote, posted in the last week, and require 3+ years experience"

# Missing constraints
"Find Python jobs"
```

### Specify Output Format

```bash
# Good
"Create a comparison table of the top 3 project management tools with pricing, features, and user ratings"

# Unclear output
"Compare project management tools"
```

### Break Down Complex Tasks

```bash
# Good approach - let the agent handle the complexity
"Research electric vehicle market trends: find sales data for Tesla, Ford, and GM from the past quarter, compare their growth rates, and identify which company is gaining market share fastest"

# The agent will automatically break this down into steps
```
