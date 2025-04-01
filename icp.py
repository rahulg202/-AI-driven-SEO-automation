import streamlit as st
import json
import os
import random
import time
import google.generativeai as genai
from typing import Dict, Any, List
import re

# Set page configuration at the very beginning
if __name__ == "__main__":
    st.set_page_config(
        page_title="ICP Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

class ICPChatbot:
    def __init__(self, api_key=None):
        # Initialize Gemini
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # For development - use environment variable
            api_key = os.environ.get("GEMINI_API_KEY", "")
            if api_key:
                genai.configure(api_key=api_key)
        
        # Define the complete form structure based on all schemas
        self.form_structure = [
            # Business Information Section
            [
                {
                    'key': 'company_name',
                    'question': '👋 Hello! Let\'s start by understanding your business. What is your company name?',
                    'type': 'text',
                    'required': True,
                    'placeholder': 'Enter your company name',
                    'section': 'business_information',
                    'evaluation_criteria': 'Check if the user has provided a clear company name. If it\'s too vague or generic, ask for clarification.'
                },
                {
                    'key': 'website_url',
                    'question': '🌐 Great! Could you share your company\'s website URL?',
                    'type': 'text',
                    'required': True,
                    'placeholder': 'https://www.yourcompany.com',
                    'section': 'business_information',
                    'evaluation_criteria': 'Verify if it looks like a valid URL or if they explicitly mentioned not having a website yet. Follow up if the format doesn\'t resemble a URL or if more information would be helpful.'
                },
                {
                    'key': 'industry',
                    'question': '🏢 Which industry does your business belong to?',
                    'type': 'text',
                    'required': True,
                    'placeholder': 'E.g., Fashion, Electronics, Food & Beverage, etc.',
                    'section': 'business_information',
                    'evaluation_criteria': 'Check if the user has specified a clear industry. If it\'s too broad or vague, ask for more specificity.'
                },
                {
                    'key': 'business_description',
                    'question': '📝 Could you provide a brief description of your business?',
                    'type': 'textarea',
                    'required': True,
                    'placeholder': 'Tell me about what your business does, your products/services, and your value proposition...',
                    'section': 'business_information',
                    'evaluation_criteria': 'Evaluate if the description includes what they do, their products/services, and their value proposition. If any of these elements are missing, ask specifically about them.'
                }
            ],
            # Target Audience Section
            [
                {
                    'key': 'age_group',
                    'question': '👥 What age groups are you targeting?',
                    'type': 'multi-select',
                    'options': ["18-24", "25-34", "35-44", "45-54", "55+"],
                    'required': True,
                    'section': 'target_audience',
                    'evaluation_criteria': 'Check if they\'ve selected at least one age group. If they\'ve selected too many (all), ask if they have a primary focus.'
                },
                {
                    'key': 'gender',
                    'question': '⚧ Which gender demographics are you primarily targeting?',
                    'type': 'multi-select',
                    'options': ["Male", "Female", "Other"],
                    'required': True,
                    'section': 'target_audience',
                    'evaluation_criteria': 'Verify they\'ve made a selection. If they\'ve selected all options, check if they have more specific targeting within these groups.'
                },
                {
                    'key': 'profession',
                    'question': '💼 What professions or occupations do your ideal customers have?',
                    'type': 'text',
                    'required': True,
                    'placeholder': 'E.g., professionals, students, stay-at-home parents, etc.',
                    'section': 'target_audience',
                    'evaluation_criteria': 'Determine if they\'ve provided specific professions or if they\'ve been too general. Ask for more specificity if needed.'
                },
                {
                    'key': 'interests_pain_points',
                    'question': '🤔 What are the main interests, pain points, or challenges your customers face?',
                    'type': 'textarea',
                    'required': True,
                    'placeholder': 'Describe their problems, interests, and what motivates them...',
                    'section': 'target_audience',
                    'evaluation_criteria': 'Evaluate if they\'ve included both interests and pain points or challenges. If they\'ve focused on only one aspect, ask about the other.'
                },
                {
                    'key': 'geo_regions',
                    'question': '🌎 Which geographic regions are you targeting?',
                    'type': 'multi-select',
                    'options': ["Specific Countries", "Specific Cities", "Global"],
                    'required': True,
                    'section': 'target_audience',
                    'evaluation_criteria': 'If they select "Specific Countries" or "Specific Cities", ask them to name those specific locations.'
                },
                {
                    'key': 'purchasing_behavior',
                    'question': '🛒 How do your customers typically make purchases?',
                    'type': 'dropdown',
                    'options': ["Online", "In-store", "Both"],
                    'required': True,
                    'section': 'target_audience',
                    'evaluation_criteria': 'For "Both", ask if one channel is more dominant than the other. For "Online" or "In-store", ask for more details about their specific purchasing process.'
                }
            ],
            # SEO Goals Section
            [
                {
                    'key': 'main_goals',
                    'question': '🎯 What are your main SEO goals?',
                    'type': 'multi-select',
                    'options': [
                        "Increase organic traffic", "Rank for specific keywords",
                        "Boost sales and conversions", "Improve brand visibility",
                        "Reduce bounce rate", "Other"
                    ],
                    'required': True,
                    'section': 'seo_goals',
                    'evaluation_criteria': 'If they select "Other", ask them to specify. If they select multiple goals, ask which is their highest priority.'
                },
                {
                    'key': 'seo_type',
                    'question': '📍 Are you focusing on local or global SEO?',
                    'type': 'dropdown',
                    'options': ["Local SEO", "Global SEO"],
                    'required': True,
                    'section': 'seo_goals',
                    'evaluation_criteria': 'For "Local SEO", ask about the specific localities. For "Global SEO", ask if there are certain regions or countries of higher priority.'
                },
                {
                    'key': 'target_keywords',
                    'question': '🔍 What are your target keywords or phrases?',
                    'type': 'textarea',
                    'required': True,
                    'placeholder': 'List your top keywords or phrases you want to rank for...',
                    'section': 'seo_goals',
                    'evaluation_criteria': 'Check if they\'ve provided specific keywords or only general themes. If too vague, ask for more specific keywords. If they seem unsure, ask about their products/services and what customers might search for.'
                }
            ],
            # Competitor Analysis Section
            [
                {
                    'key': 'main_competitors',
                    'question': '🏆 Who are your main competitors in the market?',
                    'type': 'textarea',
                    'required': True,
                    'placeholder': 'List your top competitors and what makes them strong...',
                    'section': 'competitor_analysis',
                    'evaluation_criteria': 'Verify if they\'ve named specific competitors and provided some analysis of their strengths. If not, ask for more details about what makes these competitors successful.'
                },
                {
                    'key': 'competitor_websites',
                    'question': '🔗 What are the websites of your main competitors?',
                    'type': 'textarea',
                    'required': True,
                    'placeholder': 'List competitor website URLs (one per line)...',
                    'section': 'competitor_analysis',
                    'evaluation_criteria': 'Check if they\'ve provided actual URLs. If not, ask specifically for the websites of the competitors they mentioned.'
                }
            ],
            # Content Preferences Section
            [
                {
                    'key': 'tone',
                    'question': '🗣 What tone of voice do you prefer for your content?',
                    'type': 'dropdown',
                    'options': [
                        "Formal", "Conversational", "Technical",
                        "Persuasive", "Informative"
                    ],
                    'required': True,
                    'section': 'content_preferences',
                    'evaluation_criteria': 'Ask for examples of content they admire or that reflects the tone they\'re looking for.'
                },
                {
                    'key': 'content_types',
                    'question': '📊 What types of content are you interested in?',
                    'type': 'multi-select',
                    'options': [
                        "Blogs/Articles", "Videos", "Infographics",
                        "Case Studies", "Webinars", "Podcasts"
                    ],
                    'required': True,
                    'section': 'content_preferences',
                    'evaluation_criteria': 'If they select multiple types, ask which they want to prioritize or which has performed best for them in the past.'
                },
                {
                    'key': 'existing_content',
                    'question': '📚 Do you already have existing content?',
                    'type': 'radio',
                    'options': ["Yes", "No"],
                    'required': True,
                    'section': 'content_preferences',
                    'evaluation_criteria': 'If "Yes", ask what type of content they already have and how it\'s performing. If "No", ask if they\'ve thought about what kind of content would best serve their audience.'
                }
            ]
        ]
        
        # Section titles and descriptions for better organization
        self.sections = {
            'business_information': {
                'title': 'Business Information',
                'description': 'Basic information about your business to help us understand your company better.'
            },
            'target_audience': {
                'title': 'Target Audience',
                'description': 'Information about your ideal customers to create targeted content and strategies.'
            },
            'seo_goals': {
                'title': 'SEO Goals',
                'description': 'Your search engine optimization objectives and keyword strategy.'
            },
            'competitor_analysis': {
                'title': 'Competitor Analysis',
                'description': 'Details about your main competitors to help position your content effectively.'
            },
            'content_preferences': {
                'title': 'Content Preferences',
                'description': 'Your preferences for content style and format to ensure we deliver what you need.'
            }
        }
        
        # Critical fields that require follow-up if not adequate
        self.critical_fields = [
            'website_url',       # URL pattern validation
            'target_keywords',   # Need minimum keywords for SEO
            'main_competitors'   # Need competitor information for analysis
        ]
        
        # Initialize Gemini model if API key is available
        self.model = None
        if api_key:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                st.error(f"Error initializing Gemini model: {e}")
                
    def initialize_session_state(self):
        """Ensure all required session state variables are initialized"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {}
        
        if 'current_section' not in st.session_state:
            st.session_state.current_section = 0
        
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
        
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
            
        if 'follow_up_mode' not in st.session_state:
            st.session_state.follow_up_mode = False
            
        if 'follow_up_for' not in st.session_state:
            st.session_state.follow_up_for = None
            
        if 'section_transitions' not in st.session_state:
            st.session_state.section_transitions = {}
            
        if 'insights' not in st.session_state:
            st.session_state.insights = {}
            
        if 'input_key' not in st.session_state:
            st.session_state.input_key = 0
            
        if 'form_complete' not in st.session_state:
            st.session_state.form_complete = False
            
        if 'gemini_chat' not in st.session_state:
            st.session_state.gemini_chat = None
            
        if 'follow_up_questions' not in st.session_state:
            st.session_state.follow_up_questions = {}

    def evaluate_with_gemini(self, question_data, answer):
        """Use Gemini to evaluate the user's answer and decide if follow-up is needed"""
        if not self.model:
            # Fall back to basic validation if Gemini isn't available
            return self.basic_validate_response(question_data, answer)
        
        question_key = question_data['key']
        question_type = question_data['type']
        evaluation_criteria = question_data.get('evaluation_criteria', '')
        
        # For empty answers in required fields
        if question_data.get('required', False):
            if isinstance(answer, list) and not answer:
                return {
                    'is_valid': False,
                    'feedback': "Please select at least one option to continue.",
                    'follow_up': None
                }
            elif not isinstance(answer, list) and (not answer or answer.strip() == ""):
                return {
                    'is_valid': False,
                    'feedback': "Please provide an answer to continue.",
                    'follow_up': None
                }
        
        # Format the answer for Gemini
        answer_text = answer if isinstance(answer, str) else ", ".join(answer) if answer else "No selection"
        
        prompt = f"""
        As an ICP (Ideal Customer Profile) chatbot agent, evaluate the user's response to the following question:
        
        Question: {question_data['question']}
        User's answer: {answer_text}
        
        Evaluation criteria: {evaluation_criteria}
        
        Think step-by-step:
        1. Is the answer sufficient and directly addresses the question?
        2. Does it meet the evaluation criteria?
        3. Is it specific enough to be actionable?
        4. Could more detailed information significantly improve our understanding?
        
        Based on this analysis, decide:
        - If the answer is satisfactory: Respond with "SATISFACTORY: [brief reasoning]"
        - If the answer needs more information: Respond with "FOLLOW_UP: [1-2 sentence follow-up question]"
        
        Keep your response brief and focused. If suggesting a follow-up, make it conversational and build on their existing answer.
        """
        
        try:
            response = self.model.generate_content(prompt)
            evaluation_text = response.text.strip()
            
            # Process the Gemini response
            if evaluation_text.startswith("SATISFACTORY:"):
                return {
                    'is_valid': True, 
                    'feedback': None,
                    'follow_up': None
                }
            elif evaluation_text.startswith("FOLLOW_UP:"):
                follow_up_question = evaluation_text.replace("FOLLOW_UP:", "").strip()
                return {
                    'is_valid': True,  # The answer is valid, but we want more info
                    'feedback': None,
                    'follow_up': follow_up_question
                }
            else:
                # Fallback if Gemini doesn't format as expected
                if "follow up" in evaluation_text.lower() or "more information" in evaluation_text.lower():
                    # Try to extract a follow-up question
                    sentences = re.split(r'[.!?]', evaluation_text)
                    for sentence in sentences:
                        if '?' in sentence:
                            follow_up = sentence.strip() + '?'
                            return {
                                'is_valid': True,
                                'feedback': None,
                                'follow_up': follow_up
                            }
                    
                    # If no question found, create a generic one
                    return {
                        'is_valid': True,
                        'feedback': None,
                        'follow_up': f"Could you provide a bit more detail about {question_key.replace('_', ' ')}?"
                    }
                    
                return {'is_valid': True, 'feedback': None, 'follow_up': None}
                
        except Exception as e:
            st.error(f"Error evaluating with Gemini: {e}")
            # Fall back to basic validation
            return self.basic_validate_response(question_data, answer)

    def basic_validate_response(self, question_data, answer):
        """Basic validation function as fallback when Gemini is unavailable"""
        # Get question type and key
        question_type = question_data['type']
        question_key = question_data['key']
        
        # For multi-select, check if anything was selected
        if question_type == 'multi-select' and isinstance(answer, list):
            if not answer:
                return {
                    'is_valid': False,
                    'feedback': "Please select at least one option to continue.",
                    'follow_up': None
                }
            return {'is_valid': True, 'feedback': None, 'follow_up': None}
            
        # For dropdown and radio, it's always valid as long as something is selected
        if question_type in ['dropdown', 'radio']:
            return {'is_valid': True, 'feedback': None, 'follow_up': None}
            
        # For text and textarea, check if empty
        if not answer or answer.strip() == "":
            return {
                'is_valid': False,
                'feedback': f"Please provide an answer to continue.",
                'follow_up': None
            }
            
        # Only apply strict validation for critical fields
        if question_key in self.critical_fields:
            if question_key == 'website_url' and not any(x in answer.lower() for x in ['.com', '.org', '.net', '.io', 'http', 'www']):
                if 'none' not in answer.lower() and 'no website' not in answer.lower() and 'not yet' not in answer.lower():
                    return {
                        'is_valid': False,
                        'feedback': "That doesn't look like a website URL. Please provide a valid URL or specify if you don't have a website yet.",
                        'follow_up': None
                    }
                    
            if question_key == 'target_keywords' and len(answer.split()) < 2:
                return {
                    'is_valid': False,
                    'feedback': "Please provide at least a couple of keywords to help us understand your SEO goals.",
                    'follow_up': None
                }
                
            if question_key == 'main_competitors' and len(answer.strip()) < 3:
                return {
                    'is_valid': False,
                    'feedback': "Please mention at least one competitor to help us understand your market position.",
                    'follow_up': None
                }
        
        # Default: valid
        return {'is_valid': True, 'feedback': None, 'follow_up': None}
    
    def generate_transition_message(self, from_section, to_section):
        """Generate a transition message between sections"""
        transitions = {
            'business_information_to_target_audience': [
                f"Now let's understand who your customers are.",
                f"Let's talk about your target audience.",
                f"Next, tell me about the people you're trying to reach."
            ],
            'target_audience_to_seo_goals': [
                f"Let's discuss your SEO objectives.",
                f"Now, about your SEO goals.",
                f"Let's talk about what you want to achieve with SEO."
            ],
            'seo_goals_to_competitor_analysis': [
                f"Let's analyze your competition now.",
                f"Tell me about your competitors.",
                f"Let's understand your competitive landscape."
            ],
            'competitor_analysis_to_content_preferences': [
                f"Finally, let's discuss your content preferences.",
                f"Last section: your content preferences.",
                f"Let's finish with your content needs."
            ]
        }
        
        # Generate key for the transition
        key = f"{from_section}to{to_section}"
        
        # If we have predefined transitions, use them
        if key in transitions:
            return random.choice(transitions[key])
            
        # Default transition
        return f"Let's move on to {self.sections[to_section]['title']}."

    def display_conversation_history(self):
        """Display the entire conversation history"""
        for msg in st.session_state.conversation_history:
            role = msg['role']
            content = msg['content']
            
            if role == 'user':
                st.chat_message('user').write(content)
            else:
                st.chat_message('assistant').write(content)
    
    def render_current_question(self, question_data):
        """Render the current question in the chat"""
        st.chat_message('assistant').write(question_data['question'])
    
    def process_user_answer(self, question_data, answer):
        """Process the user's answer and determine next steps with agentic thinking"""
        # Get question information
        question_key = question_data['key']
        section = question_data.get('section', 'general')
        
        # Add user's answer to conversation history
        st.session_state.conversation_history.append({
            'role': 'user',
            'content': answer,
            'key': question_key
        })
        
        # Check if we're in follow-up mode from a previous question
        if st.session_state.follow_up_mode and st.session_state.follow_up_for:
            original_key = st.session_state.follow_up_for
            
            # For follow-ups, we add the answer as additional context
            if isinstance(st.session_state.form_data.get(original_key, ""), list):
                # If the original answer was a list (for multi-select), we keep it as is
                # and just note the follow-up separately
                if 'follow_ups' not in st.session_state.form_data:
                    st.session_state.form_data['follow_ups'] = {}
                
                if original_key not in st.session_state.form_data['follow_ups']:
                    st.session_state.form_data['follow_ups'][original_key] = []
                
                st.session_state.form_data['follow_ups'][original_key].append(answer)
            else:
                # For text answers, we can append the follow-up information
                st.session_state.form_data[original_key] = st.session_state.form_data.get(original_key, "") + "\n\nAdditional Info: " + answer
            
            # Store this follow-up in our tracking
            if original_key not in st.session_state.follow_up_questions:
                st.session_state.follow_up_questions[original_key] = []
            
            st.session_state.follow_up_questions[original_key].append({
                'question': st.session_state.conversation_history[-2]['content'],
                'answer': answer
            })
                
            # Reset follow-up mode
            st.session_state.follow_up_mode = False
            st.session_state.follow_up_for = None
            
            # Move to next question
            st.session_state.current_question += 1
            
            # Check if we've completed a section
            if st.session_state.current_question >= len(self.form_structure[st.session_state.current_section]):
                self.handle_section_transition()
                
            # Increment the input key to ensure fresh input widgets
            st.session_state.input_key += 1
            st.rerun()
            return
        
        # Save the answer in form data
        st.session_state.form_data[question_key] = answer
        
        # Use Gemini to evaluate the response
        evaluation_result = self.evaluate_with_gemini(question_data, answer)
        
        # If the answer is invalid, ask for clarification
        if not evaluation_result['is_valid'] and evaluation_result['feedback']:
            # Add feedback to conversation history
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': evaluation_result['feedback'],
                'key': f"{question_key}_feedback"
            })
            
            # Store that we're in follow-up mode for this question
            st.session_state.follow_up_mode = True
            st.session_state.follow_up_for = question_key
            
            # Increment the input key for fresh input widget
            st.session_state.input_key += 1
            st.rerun()
            return
        
        # If Gemini suggests a follow-up question
        if evaluation_result['follow_up']:
            # Add follow-up question to conversation history
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': evaluation_result['follow_up'],
                'key': f"{question_key}_follow_up"
            })
            
            # Store that we're in follow-up mode for this question
            st.session_state.follow_up_mode = True
            st.session_state.follow_up_for = question_key
            
            # Track the follow-up question
            if question_key not in st.session_state.follow_up_questions:
                st.session_state.follow_up_questions[question_key] = []
            
            # Increment the input key for fresh input widget
            st.session_state.input_key += 1
            st.rerun()
            return
        
        # Move to next question if no follow-up needed
        st.session_state.current_question += 1
        
        # Check if we've completed a section
        if st.session_state.current_question >= len(self.form_structure[st.session_state.current_section]):
            self.handle_section_transition()
                
        # Increment the input key to ensure fresh input widgets
        st.session_state.input_key += 1
                
        # Rerun to refresh the page with the new question
        st.rerun()
    
    def handle_section_transition(self):
        """Handle the transition between sections"""
        # Get current and next section names
        if st.session_state.current_section < len(self.form_structure) - 1:
            current_section_questions = self.form_structure[st.session_state.current_section]
            next_section_questions = self.form_structure[st.session_state.current_section + 1]
            
            if current_section_questions and next_section_questions:
                from_section = current_section_questions[0].get('section', 'general')
                to_section = next_section_questions[0].get('section', 'general')
                
                # Generate transition message
                transition_msg = self.generate_transition_message(from_section, to_section)
                
                # Add section transition to conversation
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': transition_msg,
                    'key': f"transition_{st.session_state.current_section}"
                })
        
        # Move to next section
        st.session_state.current_section += 1
        st.session_state.current_question = 0
        
        # If we've completed all sections, mark form as complete
        if st.session_state.current_section >= len(self.form_structure):
            st.session_state.form_complete = True
    
    def handle_user_input(self, question_data):
        """Handle user input based on question type"""
        question_type = question_data['type']
        
        if question_type == 'text' or question_type == 'textarea':
            # Get the placeholder text
            input_placeholder = question_data.get('placeholder', 'Enter your response')
            
            # Use chat_input which supports pressing Enter to submit
            user_input = st.chat_input(placeholder=input_placeholder, key=f"chat_input_{st.session_state.input_key}")
            
            # Process input if provided
            if user_input:
                self.process_user_answer(question_data, user_input)
                
        elif question_type == 'dropdown':
            # Create a container for the dropdown
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_option = st.selectbox(
                    label="Select an option:",
                    options=question_data['options'],
                    key=f"select_{question_data['key']}_{st.session_state.input_key}"
                )
            
            with col2:
                # Regular button for dropdown submission
                submit_button = st.button(
                    "Submit",
                    key=f"submit_{question_data['key']}_{st.session_state.input_key}"
                )
                
                if submit_button:
                    self.process_user_answer(question_data, selected_option)
                    
        elif question_type == 'multi-select':
            # Create a container for the multi-select
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_options = st.multiselect(
                    label="Select all that apply:",
                    options=question_data['options'],
                    key=f"multiselect_{question_data['key']}_{st.session_state.input_key}"
                )
            
            with col2:
                # Regular button for multi-select submission
                submit_button = st.button(
                    "Submit",
                    key=f"submit_{question_data['key']}_{st.session_state.input_key}"
                )
                
                if submit_button:
                    self.process_user_answer(question_data, selected_options)
                    
        elif question_type == 'radio':
            # Create a container for the radio buttons
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_option = st.radio(
                    label="Select one option:",
                    options=question_data['options'],
                    key=f"radio_{question_data['key']}_{st.session_state.input_key}"
                )
            
            with col2:
                # Regular button for radio submission
                submit_button = st.button(
                    "Submit",
                    key=f"submit_{question_data['key']}_{st.session_state.input_key}"
                )
                
                if submit_button:
                    self.process_user_answer(question_data, selected_option)
    
    def render_form(self):
        """Render the full form interface with all questions and responses"""
        # Ensure session state is initialized
        self.initialize_session_state()
        
        # Display the full conversation history first
        self.display_conversation_history()
        
        # If form is not complete, show the current question
        if st.session_state.current_section < len(self.form_structure):
            # Get current section and question
            current_section = self.form_structure[st.session_state.current_section]
            
            if st.session_state.current_question < len(current_section):
                current_question = current_section[st.session_state.current_question]
                
                # Check if we're starting a new section (except the first section)
                if st.session_state.current_question == 0 and st.session_state.current_section > 0:
                    # Get section key
                    section_key = current_question.get('section', 'general')
                    
                    # If we haven't shown the section header yet
                    section_header_key = f"section_header_{section_key}"
                    if section_header_key not in st.session_state.section_transitions:
                        # Mark that we've shown this section header
                        st.session_state.section_transitions[section_header_key] = True
                        
                        # Get section info
                        section_info = self.sections.get(section_key, {'title': 'Next Section', 'description': ''})
                        
                        # Display section header
                        st.subheader(f"📋 {section_info['title']}")
                        st.write(section_info['description'])
                
                # Display the current question if it's not already in the history
                if not any(msg.get('content') == current_question['question'] and msg.get('role') == 'assistant' 
                          for msg in st.session_state.conversation_history[-2:]):
                    self.render_current_question(current_question)
                    
                    # Add question to conversation history as assistant message
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': current_question['question'],
                        'key': f"{current_question['key']}_question"
                    })
                
                # Handle user input for the current question
                self.handle_user_input(current_question)
    
    def generate_insights(self):
        """Generate business insights based on collected data and follow-up responses"""
        insights = []
        
        # Get key data from form
        company_name = st.session_state.form_data.get('company_name', 'your company')
        industry = st.session_state.form_data.get('industry', '')
        
        # Age group insights
        age_groups = st.session_state.form_data.get('age_group', [])
        if age_groups:
            if set(age_groups) & set(["18-24", "25-34"]):
                insights.append(f"Your focus on younger demographics suggests social media platforms like Instagram and TikTok could be valuable channels.")
            if set(age_groups) & set(["45-54", "55+"]):
                insights.append(f"Your target audience includes older demographics who typically value reliability and detailed information.")
        
        # SEO insights
        seo_goals = st.session_state.form_data.get('main_goals', [])
        if seo_goals:
            if "Increase organic traffic" in seo_goals and "Boost sales and conversions" in seo_goals:
                insights.append(f"Your focus on both traffic and conversions suggests a need for content that balances SEO optimization with strong calls-to-action.")
        
        # Content insights
        content_types = st.session_state.form_data.get('content_types', [])
        if content_types:
            if "Blogs/Articles" in content_types and "Case Studies" in content_types:
                insights.append(f"Your interest in both blogs and case studies suggests a good opportunity for a pillar content strategy with detailed educational resources.")
        
        # Competitive insights
        competitors = st.session_state.form_data.get('main_competitors', '')
        if competitors and len(competitors.strip()) > 0:
            insights.append(f"A competitive analysis of your mentioned competitors will help identify content gaps and opportunities.")
        
        # Use follow-up data for deeper insights if available
        if hasattr(st.session_state, 'follow_up_questions') and st.session_state.follow_up_questions:
            # Look for specific follow-up responses
            for key, follow_ups in st.session_state.follow_up_questions.items():
                if key == 'geo_regions' and len(follow_ups) > 0:
                    insights.append(f"Your specific regional focus will benefit from localized content and region-specific SEO strategies.")
                
                if key == 'profession' and len(follow_ups) > 0:
                    insights.append(f"Creating content that addresses the specific professional challenges of your target audience will increase engagement.")
                    
                if key == 'interests_pain_points' and len(follow_ups) > 0:
                    insights.append(f"Addressing the specific pain points you've identified in your content will help establish your authority and relevance.")
        
        # Enhance with Gemini insights if available
        if self.model and len(insights) > 0:
            try:
                # Generate additional strategic insight
                form_data_str = json.dumps(st.session_state.form_data, indent=2)
                prompt = f"""
                As a strategic marketing analyst, review this ICP (Ideal Customer Profile) data:
                
                {form_data_str}
                
                Provide ONE additional strategic insight that isn't covered by these existing insights:
                {insights}
                
                Your insight should be:
                1. Specific to the business and market
                2. Actionable for content or SEO strategy
                3. Written as a single paragraph (2-3 sentences max)
                4. Start with an action verb
                """
                
                response = self.model.generate_content(prompt)
                if response.text:
                    additional_insight = response.text.strip()
                    insights.append(additional_insight)
            except Exception as e:
                # Continue with existing insights if Gemini fails
                pass
        
        # Add general insight if we have few specific ones
        if len(insights) < 3:
            insights.append(f"Based on your industry ({industry}), creating content that addresses specific pain points will help establish {company_name} as an authority.")
        
        return insights
    
    def save_form_data(self):
        """Save the completed form data to a JSON file"""
        # Ensure directory exists
        os.makedirs('icp_submissions', exist_ok=True)
        
        # Generate unique filename
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        company_name = st.session_state.form_data.get('company_name', 'unknown').lower().replace(' ', '_')
        filename = f"icp_submissions/icp_{company_name}_{timestamp}.json"
        
        # Generate insights
        insights = self.generate_insights()
        
        # Save JSON file with data
        submission_data = {
            'form_data': st.session_state.form_data,
            'follow_up_data': st.session_state.follow_up_questions if hasattr(st.session_state, 'follow_up_questions') else {},
            'insights': insights,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sections': list(self.sections.keys())
        }
        
        with open(filename, 'w') as f:
            json.dump(submission_data, f, indent=4)
        
        return filename, insights

def main():
    # Set up sidebar for API key input
    with st.sidebar:
        st.title("🤖 Settings")
        api_key = st.text_input("Enter your Gemini API key (optional)", type="password")
        st.caption("If no API key is provided, the chatbot will use basic validation logic.")
        
        if api_key:
            st.success("API key provided! Gemini AI will be used for intelligent follow-ups.")
    
    # Check if the app is already initialized
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
    # Set up page title and header
    st.title("🤖 ICP Chatbot: Discover Your Business Profile")
    st.write("Let's build your Ideal Customer Profile through an interactive conversation. Just press Enter to submit your text answers.")
    
    # Initialize the chatbot with API key if provided
    chatbot = ICPChatbot(api_key=api_key)
    
    # Render the form or show completion message
    if not st.session_state.get('form_complete', False):
        chatbot.render_form()
    else:
        # Save form data and get insights
        filename, insights = chatbot.save_form_data()
        
        # Display full conversation history before completion message
        chatbot.display_conversation_history()
        
        # Final thank you message
        st.balloons()
        st.success(f"🎉 Thank you for completing the ICP form! We've saved your business insights to {filename}.")
        
        # Show insights
        st.subheader("🧠 Key Insights for Your Business")
        for i, insight in enumerate(insights, 1):
            st.markdown(f"{i}.** {insight}")
        st.write("---")
        
        # Show a summary of collected data
        st.subheader("📊 Summary of Your Business Profile")
        
        # Organize data by sections
        organized_data = {}
        for section_name, section_info in chatbot.sections.items():
            organized_data[section_info['title']] = {}
            
            # Find all questions for this section
            for section in chatbot.form_structure:
                for question in section:
                    if question.get('section') == section_name and question['key'] in st.session_state.form_data:
                        # Get the answer
                        answer = st.session_state.form_data[question['key']]
                        
                        # Add question and answer to the organized data
                        organized_data[section_info['title']][question['question']] = {
                            'answer': answer,
                            'follow_ups': st.session_state.follow_up_questions.get(question['key'], [])
                        }
        
        # Display organized summary with expanders for each section
        for section_title, questions in organized_data.items():
            with st.expander(f"{section_title}", expanded=True):
                for question, data in questions.items():
                    st.write(f"{question}")
                    
                    # Format the answer based on type
                    answer = data['answer']
                    if isinstance(answer, list):
                        # For multi-select answers, display as bullet points
                        if answer:
                            for item in answer:
                                st.write(f"- {item}")
                        else:
                            st.write("No selection made")
                    else:
                        st.write(answer)
                    
                    # Display follow-up Q&A if any
                    follow_ups = data['follow_ups']
                    if follow_ups:
                        with st.container():
                            st.markdown("*Follow-up information:*")
                            for fu in follow_ups:
                                if isinstance(fu, dict) and 'question' in fu and 'answer' in fu:
                                    st.markdown(f"{fu['question']}")
                                    st.markdown(f"Response: {fu['answer']}")
                    
                    st.write("---")
        
        # Reset button
        if st.button("Start New ICP Analysis"):
            # Reset form state
            st.session_state.form_data = {}
            st.session_state.current_section = 0
            st.session_state.current_question = 0
            st.session_state.conversation_history = []
            st.session_state.follow_up_mode = False
            st.session_state.follow_up_for = None
            st.session_state.section_transitions = {}
            st.session_state.insights = {}
            st.session_state.input_key = 0  
            st.session_state.form_complete = False
            st.session_state.follow_up_questions = {}
            st.rerun()

if __name__ == "__main__":
    main()