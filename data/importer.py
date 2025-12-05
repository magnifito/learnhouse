#!/usr/bin/env python3
"""
LearnHouse Course Importer

Imports validated course data JSON files into the LearnHouse platform.
Supports all activity types (video, document, dynamic, assignment) and all block types.
"""

import argparse
import json
import requests
import sys
import uuid
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import jsonschema
from jsonschema import validate, ValidationError


# Validation functions
def load_schema(schema_path: str = None) -> Dict[str, Any]:
    """Load the JSON schema from file."""
    if schema_path is None:
        schema_path = Path(__file__).parent / "course-schema.json"
    
    with open(schema_path, 'r') as f:
        return json.load(f)


def load_course_data(file_path: str) -> Dict[str, Any]:
    """Load course data from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def validate_activity(activity: Dict[str, Any], activity_index: int) -> List[str]:
    """Validate a single activity against type-specific requirements."""
    errors = []
    activity_type = activity.get('type', '').lower()
    activity_name = activity.get('name', f'Activity {activity_index + 1}')
    
    if activity_type == 'video':
        if 'video_url' not in activity:
            errors.append(f"  - Activity '{activity_name}': Missing required 'video_url' for video activity")
        if 'video_subtype' not in activity:
            errors.append(f"  - Activity '{activity_name}': Missing 'video_subtype' (should be 'youtube' or 'hosted')")
    
    elif activity_type == 'document':
        if 'document_url' not in activity:
            errors.append(f"  - Activity '{activity_name}': Missing required 'document_url' for document activity")
        if 'document_subtype' not in activity:
            errors.append(f"  - Activity '{activity_name}': Missing 'document_subtype' (should be 'pdf' or 'doc')")
    
    elif activity_type == 'dynamic':
        if 'blocks' not in activity or not activity.get('blocks'):
            errors.append(f"  - Activity '{activity_name}': Missing or empty 'blocks' array for dynamic activity")
    
    elif activity_type == 'assignment':
        if 'assignment' not in activity:
            errors.append(f"  - Activity '{activity_name}': Missing required 'assignment' object for assignment activity")
        else:
            assignment = activity['assignment']
            if 'tasks' in assignment and assignment['tasks']:
                for i, task in enumerate(assignment['tasks']):
                    task_title = task.get('title', f'Task {i + 1}')
                    if task.get('assignment_type') == 'QUIZ' and 'contents' not in task:
                        errors.append(f"  - Activity '{activity_name}', Task '{task_title}': QUIZ tasks should have 'contents' with questions")
    
    return errors


def validate_course_data(course_data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate course data against schema and custom business rules.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Schema validation
    try:
        validate(instance=course_data, schema=schema)
    except ValidationError as e:
        errors.append(f"Schema validation error: {e.message}")
        if e.path:
            errors.append(f"  Path: {' -> '.join(str(p) for p in e.path)}")
    
    # Custom business rule validations
    chapters = course_data.get('chapters', [])
    
    if not chapters:
        errors.append("Course must have at least one chapter")
    
    for chapter_idx, chapter in enumerate(chapters):
        chapter_name = chapter.get('name', f'Chapter {chapter_idx + 1}')
        activities = chapter.get('activities', [])
        
        if not activities:
            errors.append(f"Chapter '{chapter_name}': Must have at least one activity")
        
        for activity_idx, activity in enumerate(activities):
            activity_errors = validate_activity(activity, activity_idx)
            errors.extend(activity_errors)
    
    return len(errors) == 0, errors


class LearnHouseImporter:
    """Handles importing course data into LearnHouse platform."""
    
    def __init__(self, api_url: str, token: str, org_id: int, verbose: bool = False):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.org_id = org_id
        self.verbose = verbose
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def login(api_url: str, email: str, password: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
        """Authenticate and get access token."""
        if verbose:
            print(f"🔐 Authenticating to {api_url}...")
            print(f"   Email: {email}")
        else:
            print(f"Logging in to {api_url} as {email}...")
        response = requests.post(
            f"{api_url}/api/v1/auth/login",
            data={"username": email, "password": password}
        )
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}", file=sys.stderr)
            return None
        if verbose:
            print(f"   ✓ Authentication successful")
        return response.json()
    
    def create_course(self, course_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new course."""
        print(f"Creating course '{course_data['name']}'...")
        
        if self.verbose:
            print(f"   📝 Course details:")
            print(f"      Name: {course_data['name']}")
            print(f"      Description: {course_data.get('description', 'N/A')[:50]}...")
            print(f"      Tags: {course_data.get('tags', 'N/A')}")
            print(f"      Chapters: {len(course_data.get('chapters', []))}")
        
        data = {
            "name": course_data['name'],
            "description": course_data.get('description', ''),
            "about": course_data.get('about', ''),
            "learnings": course_data.get('learnings', ''),
            "tags": course_data.get('tags', ''),
            "public": "true",
            "thumbnail_type": "image"
        }
        
        if self.verbose:
            print(f"   📤 POST {self.api_url}/api/v1/courses/?org_id={self.org_id}")
        
        response = requests.post(
            f"{self.api_url}/api/v1/courses/?org_id={self.org_id}",
            headers=self.headers,
            data=data
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create course: {response.text}", file=sys.stderr)
            if self.verbose:
                print(f"   Status code: {response.status_code}")
            return None
        
        result = response.json()
        if self.verbose:
            print(f"   ✓ Course created (ID: {result.get('id')}, UUID: {result.get('course_uuid')})")
        
        return result
    
    def create_chapter(self, course_id: int, chapter_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new chapter."""
        print(f"  Creating chapter '{chapter_data['name']}'...")
        
        if self.verbose:
            print(f"     📝 Chapter details:")
            print(f"        Name: {chapter_data['name']}")
            print(f"        Description: {chapter_data.get('description', 'N/A')[:50]}...")
            print(f"        Activities: {len(chapter_data.get('activities', []))}")
        
        data = {
            "name": chapter_data['name'],
            "description": chapter_data.get('description', ''),
            "course_id": course_id,
            "org_id": self.org_id
        }
        
        if self.verbose:
            print(f"     📤 POST {self.api_url}/api/v1/chapters/")
        
        response = requests.post(
            f"{self.api_url}/api/v1/chapters/",
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 200:
            print(f"  ❌ Failed to create chapter: {response.text}", file=sys.stderr)
            if self.verbose:
                print(f"     Status code: {response.status_code}")
            return None
        
        result = response.json()
        if self.verbose:
            print(f"     ✓ Chapter created (ID: {result.get('id')})")
        
        return result
    
    @staticmethod
    def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
        """Parse inline markdown formatting (bold, italic, code) into Tiptap text nodes."""
        nodes = []
        i = 0
        
        while i < len(text):
            # Check for bold **text**
            bold_match = re.match(r'\*\*(.+?)\*\*', text[i:])
            if bold_match:
                nodes.append({
                    "type": "text",
                    "text": bold_match.group(1),
                    "marks": [{"type": "bold"}]
                })
                i += len(bold_match.group(0))
                continue
            
            # Check for italic *text*
            italic_match = re.match(r'\*(.+?)\*', text[i:])
            if italic_match and not text[i:].startswith('**'):
                nodes.append({
                    "type": "text",
                    "text": italic_match.group(1),
                    "marks": [{"type": "italic"}]
                })
                i += len(italic_match.group(0))
                continue
            
            # Check for code `text`
            code_match = re.match(r'`(.+?)`', text[i:])
            if code_match:
                nodes.append({
                    "type": "text",
                    "text": code_match.group(1),
                    "marks": [{"type": "code"}]
                })
                i += len(code_match.group(0))
                continue
            
            # Regular text
            if i < len(text):
                next_bold = text.find('**', i)
                next_italic = text.find('*', i) if not text[i:].startswith('*') else -1
                next_code = text.find('`', i)
                
                next_mark = len(text)
                for pos in [next_bold, next_italic, next_code]:
                    if pos != -1 and pos < next_mark:
                        next_mark = pos
                
                if next_mark > i:
                    nodes.append({
                        "type": "text",
                        "text": text[i:next_mark]
                    })
                    i = next_mark
                else:
                    nodes.append({
                        "type": "text",
                        "text": text[i]
                    })
                    i += 1
        
        return nodes if nodes else [{"type": "text", "text": text}]
    
    @staticmethod
    def convert_blocks_to_tiptap(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert course blocks format to Tiptap JSON format."""
        tiptap_content = []
        
        for block in blocks:
            block_type = block.get('type', '')
            
            if block_type == 'text':
                text_content = block.get('content', '')
                lines = text_content.split('\n')
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Empty lines
                    if not line:
                        tiptap_content.append({"type": "paragraph"})
                        i += 1
                        continue
                    
                    # Headings
                    if line.startswith('#### '):
                        tiptap_content.append({
                            "type": "heading",
                            "attrs": {"level": 4},
                            "content": LearnHouseImporter.parse_inline_formatting(line[5:].strip())
                        })
                        i += 1
                    elif line.startswith('### '):
                        tiptap_content.append({
                            "type": "heading",
                            "attrs": {"level": 3},
                            "content": LearnHouseImporter.parse_inline_formatting(line[4:].strip())
                        })
                        i += 1
                    elif line.startswith('## '):
                        tiptap_content.append({
                            "type": "heading",
                            "attrs": {"level": 2},
                            "content": LearnHouseImporter.parse_inline_formatting(line[3:].strip())
                        })
                        i += 1
                    elif line.startswith('# '):
                        tiptap_content.append({
                            "type": "heading",
                            "attrs": {"level": 1},
                            "content": LearnHouseImporter.parse_inline_formatting(line[2:].strip())
                        })
                        i += 1
                    # Bullet lists - group consecutive items
                    elif line.startswith('- ') or line.startswith('* '):
                        list_items = []
                        while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                            item_line = lines[i].strip()
                            item_text = item_line[2:].strip()
                            # Parse inline formatting in list items
                            list_items.append({
                                "type": "listItem",
                                "content": [{
                                    "type": "paragraph",
                                    "content": LearnHouseImporter.parse_inline_formatting(item_text)
                                }]
                            })
                            i += 1
                        if list_items:
                            tiptap_content.append({
                                "type": "bulletList",
                                "content": list_items
                            })
                    # Ordered lists - group consecutive items
                    elif re.match(r'^\d+\.\s+', line):
                        list_items = []
                        while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                            item_line = lines[i].strip()
                            item_text = re.sub(r'^\d+\.\s+', '', item_line).strip()
                            # Parse inline formatting in list items
                            list_items.append({
                                "type": "listItem",
                                "content": [{
                                    "type": "paragraph",
                                    "content": LearnHouseImporter.parse_inline_formatting(item_text)
                                }]
                            })
                            i += 1
                        if list_items:
                            tiptap_content.append({
                                "type": "orderedList",
                                "content": list_items
                            })
                    else:
                        tiptap_content.append({
                            "type": "paragraph",
                            "content": LearnHouseImporter.parse_inline_formatting(line)
                        })
                        i += 1
            
            elif block_type == 'quiz':
                questions = []
                for q in block.get('questions', []):
                    q_id = str(uuid.uuid4())
                    answers = []
                    for a in q.get('answers', []):
                        answers.append({
                            "answer_id": str(uuid.uuid4()),
                            "answer": a.get('answer', ''),
                            "correct": a.get('correct', False)
                        })
                    questions.append({
                        "question_id": q_id,
                        "question": q.get('question', ''),
                        "type": "multiple_choice",
                        "answers": answers
                    })
                
                tiptap_content.append({
                    "type": "blockQuiz",
                    "attrs": {"questions": questions}
                })
            
            elif block_type == 'callout_info':
                tiptap_content.append({
                    "type": "calloutInfo",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": block.get('content', '')}]
                    }]
                })
            
            elif block_type == 'callout_warning':
                tiptap_content.append({
                    "type": "calloutWarning",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": block.get('content', '')}]
                    }]
                })
            
            elif block_type == 'image':
                img_content = block.get('content', {})
                tiptap_content.append({
                    "type": "blockImage",
                    "attrs": {
                        "blockObject": None,
                        "size": {"width": 300},
                        "alignment": img_content.get('alignment', 'center'),
                        "url": img_content.get('url', ''),
                        "alt": img_content.get('alt', ''),
                        "caption": img_content.get('caption', '')
                    }
                })
            
            elif block_type == 'code_block':
                code_content = block.get('content', {})
                tiptap_content.append({
                    "type": "codeBlock",
                    "attrs": {"language": code_content.get('language', 'plaintext')},
                    "content": [{"type": "text", "text": code_content.get('code', '')}]
                })
            
            elif block_type == 'table':
                table_content = block.get('content', {})
                headers = table_content.get('headers', [])
                rows = table_content.get('rows', [])
                
                table_rows = []
                if headers:
                    header_cells = []
                    for header in headers:
                        header_text = str(header)
                        # Parse markdown formatting in headers
                        header_content = LearnHouseImporter.parse_inline_formatting(header_text)
                        header_cells.append({
                            "type": "tableHeader",
                            "content": [{
                                "type": "paragraph",
                                "content": header_content
                            }]
                        })
                    table_rows.append({"type": "tableRow", "content": header_cells})
                
                for row in rows:
                    cells = []
                    for cell in row:
                        cell_text = str(cell)
                        # Parse markdown formatting in cells
                        cell_content = LearnHouseImporter.parse_inline_formatting(cell_text)
                        cells.append({
                            "type": "tableCell",
                            "content": [{
                                "type": "paragraph",
                                "content": cell_content
                            }]
                        })
                    table_rows.append({"type": "tableRow", "content": cells})
                
                tiptap_content.append({"type": "table", "content": table_rows})
            
            elif block_type == 'badge':
                badge_content = block.get('content', {})
                tiptap_content.append({
                    "type": "badge",
                    "attrs": {
                        "text": badge_content.get('text', ''),
                        "color": badge_content.get('color', 'blue')
                    }
                })
            
            elif block_type == 'button':
                button_content = block.get('content', {})
                tiptap_content.append({
                    "type": "button",
                    "attrs": {
                        "text": button_content.get('text', ''),
                        "url": button_content.get('url', ''),
                        "style": button_content.get('style', 'primary')
                    }
                })
            
            elif block_type == 'flipcard':
                flipcard_content = block.get('content', {})
                tiptap_content.append({
                    "type": "flipcard",
                    "attrs": {
                        "front": flipcard_content.get('front', ''),
                        "back": flipcard_content.get('back', '')
                    }
                })
            
            elif block_type == 'math_equation':
                math_content = block.get('content', {})
                tiptap_content.append({
                    "type": "mathEquation",
                    "attrs": {
                        "equation": math_content.get('equation', ''),
                        "display": math_content.get('display', 'inline')
                    }
                })
            
            elif block_type == 'embedded_video':
                video_content = block.get('content', {})
                tiptap_content.append({
                    "type": "youtube",
                    "attrs": {
                        "src": video_content.get('url', ''),
                        "width": 640,
                        "height": 480
                    }
                })
            
            elif block_type == 'pdf_block':
                pdf_content = block.get('content', {})
                tiptap_content.append({
                    "type": "blockPDF",
                    "attrs": {
                        "url": pdf_content.get('url', ''),
                        "title": pdf_content.get('title', '')
                    }
                })
            
            elif block_type == 'web_preview':
                web_content = block.get('content', {})
                tiptap_content.append({
                    "type": "blockWebPreview",
                    "attrs": {
                        "url": web_content.get('url', ''),
                        "title": web_content.get('title', '')
                    }
                })
            
            elif block_type == 'scenarios':
                scenarios_content = block.get('content', {})
                tiptap_content.append({
                    "type": "scenarios",
                    "attrs": {
                        "title": scenarios_content.get('title', 'Interactive Scenario'),
                        "scenarios": scenarios_content.get('scenarios', []),
                        "currentScenarioId": scenarios_content.get('scenarios', [{}])[0].get('id', '1') if scenarios_content.get('scenarios') else '1'
                    }
                })
        
        return {"type": "doc", "content": tiptap_content}
    
    def create_activity(self, chapter_id: int, course_id: int, activity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an activity (video, document, dynamic, or assignment)."""
        activity_name = activity_data.get('name', 'Untitled Activity')
        print(f"    Creating activity '{activity_name}'...")
        
        activity_type_str = activity_data.get('type', 'dynamic').lower()
        
        if self.verbose:
            print(f"       📝 Activity details:")
            print(f"          Type: {activity_type_str}")
            print(f"          Name: {activity_name}")
            if activity_data.get('description'):
                print(f"          Description: {activity_data.get('description', '')[:50]}...")
        
        # Map activity type
        if activity_type_str == 'video':
            activity_type = "TYPE_VIDEO"
            video_subtype = activity_data.get('video_subtype', 'youtube').lower()
            activity_sub_type = "SUBTYPE_VIDEO_HOSTED" if video_subtype == 'hosted' else "SUBTYPE_VIDEO_YOUTUBE"
            
            if video_subtype == 'youtube':
                # YouTube videos need uri and type in content
                if 'video_url' in activity_data:
                    content = {
                        "uri": activity_data['video_url'],
                        "type": "youtube"
                    }
                else:
                    content = {}
            else:
                # Hosted videos need filename (but require file upload, so this will fail)
                content = {}
                if 'video_url' in activity_data:
                    print(f"      ⚠️  Hosted videos require file upload - URL will be ignored")
        
        elif activity_type_str == 'document':
            # Document activities with external URLs are converted to dynamic activities
            # since document activities require file uploads (not external URLs)
            if 'document_url' in activity_data:
                print(f"      ⚠️  Converting document activity with URL to dynamic activity")
                activity_type = "TYPE_DYNAMIC"
                activity_sub_type = "SUBTYPE_DYNAMIC_PAGE"
                # Create a dynamic activity with a heading and button linking to the PDF
                document_url = activity_data['document_url']
                document_name = activity_data.get('name', 'Document')
                document_desc = activity_data.get('description', '')
                
                # Build blocks for the dynamic activity
                blocks = []
                
                # Add heading
                if document_name:
                    blocks.append({
                        "type": "text",
                        "content": f"# {document_name}"
                    })
                
                # Add description if available
                if document_desc:
                    blocks.append({
                        "type": "text",
                        "content": document_desc
                    })
                else:
                    # Add a paragraph with a link if no description
                    blocks.append({
                        "type": "text",
                        "content": f"Click the button below to view the document, or [open it directly]({document_url})."
                    })
                
                # Add button to view PDF
                blocks.append({
                    "type": "button",
                    "content": {
                        "text": "Open Document",
                        "url": document_url,
                        "style": "primary"
                    }
                })
                
                # Include any existing blocks
                existing_blocks = activity_data.get('blocks', [])
                blocks.extend(existing_blocks)
                
                content = self.convert_blocks_to_tiptap(blocks)
            else:
                # Document activities without URLs need file uploads (not supported via JSON import)
                print(f"      ⚠️  Document activity '{activity_name}' requires file upload - skipping import")
                activity_type = "TYPE_DOCUMENT"
                doc_subtype = activity_data.get('document_subtype', 'pdf').lower()
                activity_sub_type = "SUBTYPE_DOCUMENT_DOC" if doc_subtype == 'doc' else "SUBTYPE_DOCUMENT_PDF"
                content = {}
        
        elif activity_type_str == 'assignment':
            activity_type = "TYPE_ASSIGNMENT"
            activity_sub_type = "SUBTYPE_ASSIGNMENT_ANY"
            content = {}
        
        else:  # dynamic (default)
            activity_type = "TYPE_DYNAMIC"
            activity_sub_type = "SUBTYPE_DYNAMIC_PAGE"
            content = self.convert_blocks_to_tiptap(activity_data.get('blocks', []))
        
        data = {
            "name": activity_name,
            "chapter_id": chapter_id,
            "activity_type": activity_type,
            "activity_sub_type": activity_sub_type,
            "content": content,
            "details": {},
            "published": True
        }
        
        if self.verbose:
            print(f"       📤 POST {self.api_url}/api/v1/activities/")
            print(f"          Activity type: {activity_type}")
            print(f"          Activity sub-type: {activity_sub_type}")
            if activity_type_str == 'dynamic':
                blocks_count = len(activity_data.get('blocks', []))
                print(f"          Blocks: {blocks_count}")
        
        response = requests.post(
            f"{self.api_url}/api/v1/activities/",
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 200:
            print(f"    ❌ Failed to create activity: {response.text}", file=sys.stderr)
            if self.verbose:
                print(f"       Status code: {response.status_code}")
            return None
        
        activity_result = response.json()
        activity_id = activity_result.get('id')
        activity_uuid = activity_result.get('activity_uuid')
        
        if self.verbose:
            print(f"       ✓ Activity created (ID: {activity_id}, UUID: {activity_uuid})")
        
        # For YouTube videos, update content to include activity_uuid
        if activity_type_str == 'video':
            video_subtype = activity_data.get('video_subtype', 'youtube').lower()
            if video_subtype == 'youtube' and activity_uuid:
                current_content = activity_result.get('content', {})
                if 'uri' in current_content and 'activity_uuid' not in current_content:
                    # Update content to include activity_uuid
                    updated_content = current_content.copy()
                    updated_content['activity_uuid'] = activity_uuid
                    
                    # Update the activity content
                    update_response = requests.put(
                        f"{self.api_url}/api/v1/activities/{activity_uuid}",
                        headers=self.headers,
                        json={"content": updated_content}
                    )
                    if update_response.status_code == 200:
                        activity_result = update_response.json()
                        print(f"      ✓ Updated YouTube video content with activity_uuid")
        
        # Create assignment if needed
        if activity_type_str == 'assignment' and 'assignment' in activity_data:
            self._create_assignment(course_id, chapter_id, activity_id, activity_data['assignment'])
        
        return activity_result
    
    def _create_assignment(self, course_id: int, chapter_id: int, activity_id: int, assignment_data: Dict[str, Any]):
        """Create assignment and its tasks."""
        if self.verbose:
            print(f"       📋 Creating assignment: {assignment_data.get('title', 'Untitled')}")
        
        assignment_obj = {
            "title": assignment_data.get('title', ''),
            "description": assignment_data.get('description', ''),
            "due_date": assignment_data.get('due_date', str(datetime.now() + timedelta(days=7))),
            "published": True,
            "grading_type": assignment_data.get('grading_type', 'PERCENTAGE'),
            "org_id": self.org_id,
            "course_id": course_id,
            "chapter_id": chapter_id,
            "activity_id": activity_id
        }
        
        if self.verbose:
            print(f"          📤 POST {self.api_url}/api/v1/assignments/")
            print(f"          Grading type: {assignment_data.get('grading_type', 'PERCENTAGE')}")
            tasks_count = len(assignment_data.get('tasks', []))
            print(f"          Tasks: {tasks_count}")
        
        response = requests.post(
            f"{self.api_url}/api/v1/assignments/",
            headers=self.headers,
            json=assignment_obj
        )
        
        if response.status_code != 200:
            print(f"      ❌ Failed to create assignment: {response.text}", file=sys.stderr)
            if self.verbose:
                print(f"          Status code: {response.status_code}")
            return
        
        assignment_result = response.json()
        assignment_uuid = assignment_result.get('assignment_uuid')
        print(f"      ✓ Assignment created (ID: {assignment_result.get('id')})")
        
        if self.verbose:
            print(f"          Assignment UUID: {assignment_uuid}")
        
        # Create assignment tasks
        if 'tasks' in assignment_data:
            tasks = assignment_data['tasks']
            if self.verbose:
                print(f"          📝 Creating {len(tasks)} task(s)...")
            
            for task_idx, task_data in enumerate(tasks, 1):
                if self.verbose:
                    print(f"\n          Task {task_idx}/{len(tasks)}: {task_data.get('title', 'Untitled')}")
                
                task_obj = {
                    "title": task_data.get('title', ''),
                    "description": task_data.get('description', ''),
                    "hint": task_data.get('hint', ''),
                    "reference_file": task_data.get('reference_file'),
                    "assignment_type": task_data.get('assignment_type', 'FILE_SUBMISSION'),
                    "contents": task_data.get('contents', {}),
                    "max_grade_value": task_data.get('max_grade_value', 0)
                }
                
                if self.verbose:
                    print(f"             Type: {task_data.get('assignment_type', 'FILE_SUBMISSION')}")
                    print(f"             Max grade: {task_data.get('max_grade_value', 0)}")
                    print(f"             📤 POST {self.api_url}/api/v1/assignments/{assignment_uuid}/tasks/")
                
                task_response = requests.post(
                    f"{self.api_url}/api/v1/assignments/{assignment_uuid}/tasks/",
                    headers=self.headers,
                    json=task_obj
                )
                
                if task_response.status_code == 200:
                    print(f"        ✓ Task '{task_data.get('title')}' created")
                    if self.verbose:
                        task_result = task_response.json()
                        print(f"             Task ID: {task_result.get('id')}")
                else:
                    print(f"        ❌ Failed to create task: {task_response.text}", file=sys.stderr)
                    if self.verbose:
                        print(f"             Status code: {task_response.status_code}")
    
    def import_course(self, course_data: Dict[str, Any]) -> bool:
        """Import complete course with all chapters and activities."""
        # Create course
        course = self.create_course(course_data)
        if not course:
            return False
        
        course_id = course['id']
        course_uuid = course['course_uuid']
        print(f"✓ Course created (ID: {course_id}, UUID: {course_uuid})\n")
        
        if self.verbose:
            total_chapters = len(course_data.get('chapters', []))
            total_activities = sum(len(ch.get('activities', [])) for ch in course_data.get('chapters', []))
            print(f"📊 Importing {total_chapters} chapter(s) with {total_activities} total activity(ies)\n")
        
        # Create chapters and activities
        for chapter_idx, chapter_data in enumerate(course_data.get('chapters', []), 1):
            if self.verbose:
                print(f"\n📖 Chapter {chapter_idx}/{len(course_data.get('chapters', []))}")
            
            chapter = self.create_chapter(course_id, chapter_data)
            if not chapter:
                continue
            
            chapter_id = chapter['id']
            activities = chapter_data.get('activities', [])
            
            if self.verbose:
                print(f"     📚 Processing {len(activities)} activity(ies)...")
            
            for activity_idx, activity_data in enumerate(activities, 1):
                if self.verbose:
                    print(f"\n     Activity {activity_idx}/{len(activities)}")
                self.create_activity(chapter_id, course_id, activity_data)
        
        return True


def cmd_download_images(args):
    """Download images from course data JSON file."""
    from urllib.parse import urlparse
    
    def extract_image_urls(course_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all image URLs from course data blocks."""
        images = []
        
        def process_blocks(blocks: List[Dict[str, Any]], context: str = ""):
            """Recursively process blocks to find images."""
            for block in blocks:
                block_type = block.get('type', '')
                
                if block_type == 'image':
                    img_content = block.get('content', {})
                    url = img_content.get('url', '')
                    if url:
                        images.append({
                            'url': url,
                            'alt': img_content.get('alt', ''),
                            'caption': img_content.get('caption', ''),
                            'alignment': img_content.get('alignment', 'center'),
                            'context': context
                        })
                elif block_type == 'scenarios':
                    scenarios_content = block.get('content', {})
                    for scenario in scenarios_content.get('scenarios', []):
                        image_url = scenario.get('imageUrl', '')
                        if image_url:
                            images.append({
                                'url': image_url,
                                'alt': f"Scenario image for {scenarios_content.get('title', 'Unknown')}",
                                'caption': '',
                                'alignment': 'center',
                                'context': f"{context} (scenario)"
                            })
        
        # Process all chapters and activities
        for chapter_idx, chapter in enumerate(course_data.get('chapters', []), 1):
            chapter_name = chapter.get('name', f'Chapter {chapter_idx}')
            
            for activity_idx, activity in enumerate(chapter.get('activities', []), 1):
                activity_name = activity.get('name', f'Activity {activity_idx}')
                context = f"{chapter_name} > {activity_name}"
                
                blocks = activity.get('blocks', [])
                process_blocks(blocks, context)
        
        return images
    
    def generate_filename(url: str, index: int, alt: str = "") -> str:
        """Generate a safe filename from URL or alt text."""
        # Extract photo ID from Unsplash URLs
        if 'unsplash.com' in url:
            photo_match = re.search(r'photo-([a-zA-Z0-9-]+)', url)
            if photo_match:
                photo_id = photo_match.group(1)[:12]
            else:
                photo_id = f"unsplash_{index}"
        else:
            parsed = urlparse(url)
            path = parsed.path
            if path and '.' in path:
                photo_id = Path(path).stem
            else:
                photo_id = f"image_{index}"
        
        # Clean up alt text for filename
        if alt:
            alt_clean = ''.join(c if c.isalnum() or c in '-_' else '_' for c in alt.lower()[:30])
            if alt_clean:
                return f"{photo_id}_{alt_clean}"
        
        return photo_id
    
    def download_image(url: str, filepath: Path, description: str) -> bool:
        """Download an image from URL and save it locally."""
        try:
            print(f"  Downloading: {description[:60]}...")
            
            response = requests.get(url, stream=True, timeout=30, headers={
                'User-Agent': 'LearnHouse Course Generator/1.0'
            })
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '').lower()
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                parsed = urlparse(url)
                path = parsed.path.lower()
                if '.jpg' in path or '.jpeg' in path:
                    ext = '.jpg'
                elif '.png' in path:
                    ext = '.png'
                elif '.webp' in path:
                    ext = '.webp'
                elif '.gif' in path:
                    ext = '.gif'
                else:
                    ext = '.jpg'
            
            if not filepath.suffix:
                filepath = filepath.with_suffix(ext)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = filepath.stat().st_size / 1024
            print(f"    ✓ Saved: {filepath.name} ({file_size:.1f} KB)")
            return True
            
        except Exception as e:
            print(f"    ✗ Failed: {e}", file=sys.stderr)
            return False
    
    # Load course data
    try:
        with open(args.file, 'r') as f:
            course_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found - {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract image URLs
    print(f"Extracting image URLs from {args.file}...")
    images = extract_image_urls(course_data)
    
    if not images:
        print("ℹ️  No images found in course data.")
        sys.exit(0)
    
    # Remove duplicates
    seen_urls = set()
    unique_images = []
    for img in images:
        if img['url'] not in seen_urls:
            seen_urls.add(img['url'])
            unique_images.append(img)
    
    print(f"Found {len(unique_images)} unique image(s) to download.\n")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download images and build mapping
    url_to_file = {}
    success_count = 0
    
    for idx, img_info in enumerate(unique_images, 1):
        url = img_info['url']
        filename_base = generate_filename(url, idx, img_info.get('alt', ''))
        filepath = output_dir / filename_base
        
        if filepath.exists() and not args.force:
            print(f"  [{idx}/{len(unique_images)}] Skipping (exists): {filepath.name}")
            for ext in ['.jpg', '.png', '.webp', '.gif']:
                if (output_dir / f"{filename_base}{ext}").exists():
                    filepath = output_dir / f"{filename_base}{ext}"
                    break
            url_to_file[url] = str(filepath)
            success_count += 1
            continue
        
        print(f"  [{idx}/{len(unique_images)}] {img_info.get('context', 'Image')}")
        
        if download_image(url, filepath, img_info.get('alt', url)):
            url_to_file[url] = str(filepath)
            success_count += 1
    
    # Save mapping file
    mapping_file = Path(args.mapping_file)
    mapping_data = {
        'url_to_file': url_to_file,
        'images': unique_images,
        'course_file': args.file,
        'download_date': str(datetime.now())
    }
    
    with open(mapping_file, 'w') as f:
        json.dump(mapping_data, f, indent=2)
    
    print(f"\n✅ Successfully downloaded {success_count}/{len(unique_images)} images")
    print(f"\nImages saved in: {output_dir.absolute()}")
    print(f"Mapping saved in: {mapping_file.absolute()}")

def validate_organization_data(org_data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate organization data against schema and custom business rules.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Schema validation
    try:
        validate(instance=org_data, schema=schema)
    except ValidationError as e:
        errors.append(f"Schema validation error: {e.message}")
        if e.path:
            errors.append(f"  Path: {' -> '.join(str(p) for p in e.path)}")
    
    # Custom business rule validations
    if 'slug' in org_data:
        slug = org_data['slug']
        if not re.match(r'^[a-z0-9-]+$', slug):
            errors.append(f"Invalid slug format: '{slug}' (must be lowercase alphanumeric with hyphens)")
    
    if 'email' in org_data:
        email = org_data['email']
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append(f"Invalid email format: '{email}'")
    
    # Validate config structure if present
    if 'config' in org_data:
        config = org_data['config']
        if 'features' in config:
            features = config['features']
            required_features = ['courses', 'members', 'usergroups', 'storage', 'ai', 'assignments', 
                               'payments', 'discussions', 'analytics', 'collaboration', 'api']
            for feature in required_features:
                if feature not in features:
                    errors.append(f"Missing required feature config: '{feature}'")
    
    return len(errors) == 0, errors


def cmd_validate(args):
    """Validate course data JSON file against schema."""
    # Load files
    try:
        schema = load_schema(args.schema)
        course_data = load_course_data(args.file)
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate
    if args.verbose:
        print(f"Validating: {args.file}")
        print(f"Schema: {args.schema or 'course-schema.json (default)'}")
        print()
    
    is_valid, errors = validate_course_data(course_data, schema)
    
    if is_valid:
        print("✅ Course data is valid!")
        if args.verbose:
            print(f"\nCourse: {course_data.get('name', 'Untitled')}")
            print(f"Chapters: {len(course_data.get('chapters', []))}")
            total_activities = sum(len(ch.get('activities', [])) for ch in course_data.get('chapters', []))
            print(f"Total Activities: {total_activities}")
        sys.exit(0)
    else:
        print("❌ Course data validation failed!")
        print("\nErrors found:")
        for error in errors:
            print(error)
        sys.exit(1)


def cmd_validate_org(args):
    """Validate organization data JSON file against schema."""
    # Load files
    try:
        if args.schema is None:
            schema_path = Path(__file__).parent / "organisation-schema.json"
        else:
            schema_path = Path(args.schema)
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        with open(args.file, 'r') as f:
            org_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate
    if args.verbose:
        print(f"Validating: {args.file}")
        print(f"Schema: {args.schema or 'organisation-schema.json (default)'}")
        print()
    
    is_valid, errors = validate_organization_data(org_data, schema)
    
    if is_valid:
        print("✅ Organization data is valid!")
        if args.verbose:
            print(f"\nOrganization: {org_data.get('name', 'Untitled')}")
            print(f"Slug: {org_data.get('slug', 'N/A')}")
            print(f"Email: {org_data.get('email', 'N/A')}")
            if 'config' in org_data:
                print(f"Config Version: {org_data['config'].get('config_version', 'N/A')}")
        sys.exit(0)
    else:
        print("❌ Organization data validation failed!")
        print("\nErrors found:")
        for error in errors:
            print(error)
        sys.exit(1)

def cmd_import(args):
    """Import course data into LearnHouse platform."""
    verbose = getattr(args, 'verbose', False)
    
    if verbose:
        print("=" * 60)
        print("IMPORT MODE: VERBOSE")
        print("=" * 60)
        print(f"📁 File: {args.file}")
        print(f"🌐 API URL: {args.url}")
        print(f"🏢 Organization ID: {args.org_id}")
        print()
    
    # Validate course data first (unless skipped)
    if not args.skip_validation:
        if verbose:
            print("🔍 Step 1: Validating course data...")
        else:
            print("Validating course data...")
        try:
            schema = load_schema()
            course_data = load_course_data(args.file)
            is_valid, errors = validate_course_data(course_data, schema)
            
            if not is_valid:
                print("❌ Validation failed:", file=sys.stderr)
                for error in errors:
                    print(f"  {error}", file=sys.stderr)
                print("\n💡 Tip: Run 'importer.py validate' command to see detailed errors")
                print("Use --skip-validation to import anyway (not recommended)", file=sys.stderr)
                sys.exit(1)
            
            if verbose:
                print("   ✓ Validation passed")
                print(f"   📊 Course: {course_data.get('name', 'Untitled')}")
                print(f"   📚 Chapters: {len(course_data.get('chapters', []))}")
                total_activities = sum(len(ch.get('activities', [])) for ch in course_data.get('chapters', []))
                print(f"   📝 Total Activities: {total_activities}")
                print()
            else:
                print("✓ Course data is valid\n")
        except Exception as e:
            print(f"⚠️  Validation error: {e}", file=sys.stderr)
            print("Continuing with import...\n", file=sys.stderr)
            try:
                with open(args.file, 'r') as f:
                    course_data = json.load(f)
            except Exception as e:
                print(f"❌ Error loading course data: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        print("⚠️  Skipping validation (not recommended)\n")
        with open(args.file, 'r') as f:
            course_data = json.load(f)
    
    # Authenticate
    if verbose:
        print("🔐 Step 2: Authenticating...")
    auth_result = LearnHouseImporter.login(args.url, args.email, args.password, verbose=verbose)
    if not auth_result:
        sys.exit(1)
    
    token = auth_result['tokens']['access_token']
    
    if verbose:
        print()
        print("📤 Step 3: Importing course...")
        print()
    
    # Import course
    importer = LearnHouseImporter(args.url, token, args.org_id, verbose=verbose)
    success = importer.import_course(course_data)
    
    if success:
        if verbose:
            print("\n" + "=" * 60)
        print("\n✅ Course import completed successfully!")
        if verbose:
            print("=" * 60)
    else:
        print("\n❌ Course import failed!", file=sys.stderr)
        sys.exit(1)


def cmd_import_org(args):
    """Import organization data into LearnHouse platform."""
    verbose = getattr(args, 'verbose', False)
    
    if verbose:
        print("=" * 60)
        print("ORGANIZATION IMPORT MODE: VERBOSE")
        print("=" * 60)
        print(f"📁 File: {args.file}")
        print(f"🌐 API URL: {args.url}")
        print(f"🏢 Target Org ID: {args.org_id or 'default (1)'}")
        print()
    
    # Validate organization data first (unless skipped)
    if not args.skip_validation:
        if verbose:
            print("🔍 Step 1: Validating organization data...")
        else:
            print("Validating organization data...")
        try:
            if args.schema is None:
                schema_path = Path(__file__).parent / "organisation-schema.json"
            else:
                schema_path = Path(args.schema)
            
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            with open(args.file, 'r') as f:
                org_data = json.load(f)
            
            is_valid, errors = validate_organization_data(org_data, schema)
            
            if not is_valid:
                print("❌ Validation failed:", file=sys.stderr)
                for error in errors:
                    print(f"  {error}", file=sys.stderr)
                print("\n💡 Tip: Run 'importer.py validate-org' command to see detailed errors")
                print("Use --skip-validation to import anyway (not recommended)", file=sys.stderr)
                sys.exit(1)
            
            if verbose:
                print("   ✓ Validation passed")
                print(f"   📊 Organization: {org_data.get('name', 'Untitled')}")
                print(f"   🔗 Slug: {org_data.get('slug', 'N/A')}")
                print()
            else:
                print("✓ Organization data is valid\n")
        except Exception as e:
            print(f"⚠️  Validation error: {e}", file=sys.stderr)
            print("Continuing with import...\n", file=sys.stderr)
            try:
                with open(args.file, 'r') as f:
                    org_data = json.load(f)
            except Exception as e:
                print(f"❌ Error loading organization data: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        print("⚠️  Skipping validation (not recommended)\n")
        with open(args.file, 'r') as f:
            org_data = json.load(f)
    
    # Authenticate
    if verbose:
        print("🔐 Step 2: Authenticating...")
    auth_result = LearnHouseImporter.login(args.url, args.email, args.password, verbose=verbose)
    if not auth_result:
        sys.exit(1)
    
    token = auth_result['tokens']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Determine target organization ID
    target_org_id = args.org_id
    if target_org_id is None:
        # Try to find by slug first
        org_slug = org_data.get('slug')
        if org_slug:
            if verbose:
                print(f"🔍 Looking up organization by slug: {org_slug}")
            try:
                response = requests.get(
                    f"{args.url}/api/v1/orgs/slug/{org_slug}",
                    headers=headers
                )
                if response.status_code == 200:
                    existing_org = response.json()
                    target_org_id = existing_org.get('id')
                    if verbose:
                        print(f"   ✓ Found existing organization (ID: {target_org_id})")
                else:
                    # If not found by slug, try to find by ID 1 (default org)
                    if verbose:
                        print(f"   ℹ️  Organization not found by slug, checking default org...")
                    try:
                        response = requests.get(
                            f"{args.url}/api/v1/orgs/1",
                            headers=headers
                        )
                        if response.status_code == 200:
                            target_org_id = 1
                            if verbose:
                                print(f"   ✓ Using default organization (ID: 1)")
                        else:
                            target_org_id = 1
                            if verbose:
                                print(f"   ℹ️  Will use default ID 1")
                    except:
                        target_org_id = 1
                        if verbose:
                            print(f"   ℹ️  Will use default ID 1")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Error looking up by slug: {e}")
                target_org_id = 1
        else:
            target_org_id = 1
    
    if verbose:
        print()
        print("📤 Step 3: Updating organization...")
        print(f"   Target Org ID: {target_org_id}")
        print()
    
    # Prepare organization update data (exclude config)
    org_update_data = {}
    for key in ['name', 'description', 'about', 'slug', 'email', 'label', 
                'default_locale', 'supported_locales', 'explore', 
                'logo_image', 'thumbnail_image', 'socials', 'links', 
                'scripts', 'previews']:
        if key in org_data:
            org_update_data[key] = org_data[key]
    
    # Update organization
    if verbose:
        print(f"   📝 Updating organization fields...")
        print(f"      PUT {args.url}/api/v1/orgs/{target_org_id}")
    
    response = requests.put(
        f"{args.url}/api/v1/orgs/{target_org_id}",
        headers=headers,
        json=org_update_data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to update organization: {response.text}", file=sys.stderr)
        if verbose:
            print(f"   Status code: {response.status_code}")
        sys.exit(1)
    
    if verbose:
        print(f"   ✓ Organization updated successfully")
    
    # Update organization config if provided
    if 'config' in org_data:
        if verbose:
            print()
            print("⚙️  Step 4: Updating organization configuration...")
            print(f"      PUT {args.url}/api/v1/orgs/{target_org_id}/config")
        
        config_data = org_data['config']
        
        response = requests.put(
            f"{args.url}/api/v1/orgs/{target_org_id}/config",
            headers=headers,
            json=config_data
        )
        
        if response.status_code != 200:
            print(f"⚠️  Failed to update organization config: {response.text}", file=sys.stderr)
            if verbose:
                print(f"   Status code: {response.status_code}")
            print("   Organization data was updated, but config update failed", file=sys.stderr)
        else:
            if verbose:
                print(f"   ✓ Organization configuration updated successfully")
    
    if verbose:
        print("\n" + "=" * 60)
    print("\n✅ Organization import completed successfully!")
    if verbose:
        print("=" * 60)


def cmd_publish(args):
    """Complete workflow: validate, download images, and import course data."""
    import os
    verbose = getattr(args, 'verbose', False)
    
    if verbose:
        print("=" * 60)
        print("PUBLISH MODE: VERBOSE")
        print("=" * 60)
        print(f"📁 File: {args.file}")
        print(f"🌐 API URL: {args.url}")
        print(f"🏢 Organization ID: {args.org_id}")
        if args.images_dir:
            print(f"🖼️  Images directory: {args.images_dir}")
        if args.skip_images:
            print("⚠️  Image download: SKIPPED")
        print()
    
    # Step 1: Validate
    print("=" * 60)
    print("STEP 1: Validating course data...")
    print("=" * 60)
    try:
        if verbose:
            schema_path = args.schema or "course-schema.json (default)"
            print(f"📋 Schema: {schema_path}")
            print(f"📄 Course file: {args.file}")
            print()
        
        schema = load_schema(args.schema)
        course_data = load_course_data(args.file)
        is_valid, errors = validate_course_data(course_data, schema)
        
        if not is_valid:
            print("❌ Validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  {error}", file=sys.stderr)
            print("\n💡 Fix the errors above before continuing.", file=sys.stderr)
            sys.exit(1)
        
        print("✅ Course data is valid!")
        if verbose:
            print(f"\n📊 Course details:")
            print(f"   Name: {course_data.get('name', 'Untitled')}")
            print(f"   Chapters: {len(course_data.get('chapters', []))}")
            total_activities = sum(len(ch.get('activities', [])) for ch in course_data.get('chapters', []))
            print(f"   Total Activities: {total_activities}")
        print()
    except Exception as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Step 2: Download images (if requested)
    if not args.skip_images:
        print("=" * 60)
        print("STEP 2: Downloading images...")
        print("=" * 60)
        
        # Determine output directory
        if args.images_dir:
            output_dir = Path(args.images_dir)
        else:
            # Default: data/images directory
            output_dir = Path(__file__).parent / "images"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine mapping file location
        if args.mapping_file:
            mapping_file = Path(args.mapping_file)
        else:
            # Default: image_mapping.json in data directory
            mapping_file = Path(__file__).parent / "image_mapping.json"
        
        # Extract and download images
        from urllib.parse import urlparse
        
        def extract_image_urls(course_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract all image URLs from course data blocks."""
            images = []
            
            def process_blocks(blocks: List[Dict[str, Any]], context: str = ""):
                """Recursively process blocks to find images."""
                for block in blocks:
                    block_type = block.get('type', '')
                    
                    if block_type == 'image':
                        img_content = block.get('content', {})
                        url = img_content.get('url', '')
                        if url:
                            images.append({
                                'url': url,
                                'alt': img_content.get('alt', ''),
                                'caption': img_content.get('caption', ''),
                                'alignment': img_content.get('alignment', 'center'),
                                'context': context
                            })
                    elif block_type == 'scenarios':
                        scenarios_content = block.get('content', {})
                        for scenario in scenarios_content.get('scenarios', []):
                            image_url = scenario.get('imageUrl', '')
                            if image_url:
                                images.append({
                                    'url': image_url,
                                    'alt': f"Scenario image for {scenarios_content.get('title', 'Unknown')}",
                                    'caption': '',
                                    'alignment': 'center',
                                    'context': f"{context} (scenario)"
                                })
            
            # Process all chapters and activities
            for chapter_idx, chapter in enumerate(course_data.get('chapters', []), 1):
                chapter_name = chapter.get('name', f'Chapter {chapter_idx}')
                
                for activity_idx, activity in enumerate(chapter.get('activities', []), 1):
                    activity_name = activity.get('name', f'Activity {activity_idx}')
                    context = f"{chapter_name} > {activity_name}"
                    
                    blocks = activity.get('blocks', [])
                    process_blocks(blocks, context)
            
            return images
        
        def generate_filename(url: str, index: int, alt: str = "") -> str:
            """Generate a safe filename from URL or alt text."""
            # Extract photo ID from Unsplash URLs
            if 'unsplash.com' in url:
                photo_match = re.search(r'photo-([a-zA-Z0-9-]+)', url)
                if photo_match:
                    photo_id = photo_match.group(1)[:12]
                else:
                    photo_id = f"unsplash_{index}"
            else:
                parsed = urlparse(url)
                path = parsed.path
                if path and '.' in path:
                    photo_id = Path(path).stem
                else:
                    photo_id = f"image_{index}"
            
            # Clean up alt text for filename
            if alt:
                alt_clean = ''.join(c if c.isalnum() or c in '-_' else '_' for c in alt.lower()[:30])
                if alt_clean:
                    return f"{photo_id}_{alt_clean}"
            
            return photo_id
        
        def download_image(url: str, filepath: Path, description: str) -> bool:
            """Download an image from URL and save it locally."""
            try:
                print(f"  Downloading: {description[:60]}...")
                
                response = requests.get(url, stream=True, timeout=30, headers={
                    'User-Agent': 'LearnHouse Course Generator/1.0'
                })
                response.raise_for_status()
                
                # Determine file extension
                content_type = response.headers.get('content-type', '').lower()
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    parsed = urlparse(url)
                    path = parsed.path.lower()
                    if '.jpg' in path or '.jpeg' in path:
                        ext = '.jpg'
                    elif '.png' in path:
                        ext = '.png'
                    elif '.webp' in path:
                        ext = '.webp'
                    elif '.gif' in path:
                        ext = '.gif'
                    else:
                        ext = '.jpg'
                
                if not filepath.suffix:
                    filepath = filepath.with_suffix(ext)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = filepath.stat().st_size / 1024
                print(f"    ✓ Saved: {filepath.name} ({file_size:.1f} KB)")
                return True
                
            except Exception as e:
                print(f"    ✗ Failed: {e}", file=sys.stderr)
                return False
        
        # Extract image URLs
        images = extract_image_urls(course_data)
        
        if images:
            # Remove duplicates
            seen_urls = set()
            unique_images = []
            for img in images:
                if img['url'] not in seen_urls:
                    seen_urls.add(img['url'])
                    unique_images.append(img)
            
            print(f"Found {len(unique_images)} unique image(s) to download.\n")
            
            # Download images and build mapping
            url_to_file = {}
            success_count = 0
            
            for idx, img_info in enumerate(unique_images, 1):
                url = img_info['url']
                filename_base = generate_filename(url, idx, img_info.get('alt', ''))
                filepath = output_dir / filename_base
                
                if filepath.exists() and not args.force:
                    print(f"  [{idx}/{len(unique_images)}] Skipping (exists): {filepath.name}")
                    for ext in ['.jpg', '.png', '.webp', '.gif']:
                        if (output_dir / f"{filename_base}{ext}").exists():
                            filepath = output_dir / f"{filename_base}{ext}"
                            break
                    url_to_file[url] = str(filepath)
                    success_count += 1
                    continue
                
                print(f"  [{idx}/{len(unique_images)}] {img_info.get('context', 'Image')}")
                
                if download_image(url, filepath, img_info.get('alt', url)):
                    url_to_file[url] = str(filepath)
                    success_count += 1
            
            # Save mapping file
            mapping_data = {
                'url_to_file': url_to_file,
                'images': unique_images,
                'course_file': args.file,
                'download_date': str(datetime.now())
            }
            
            with open(mapping_file, 'w') as f:
                json.dump(mapping_data, f, indent=2)
            
            print(f"\n✅ Successfully downloaded {success_count}/{len(unique_images)} images")
            print(f"Images saved in: {output_dir.absolute()}")
            print(f"Mapping saved in: {mapping_file.absolute()}\n")
        else:
            print("ℹ️  No images found in course data.\n")
    
    # Step 3: Import
    print("=" * 60)
    print("STEP 3: Importing course...")
    print("=" * 60)
    
    if verbose:
        print(f"🔐 Authenticating to {args.url}...")
        print(f"   Email: {args.email}")
        print()
    
    # Authenticate
    auth_result = LearnHouseImporter.login(args.url, args.email, args.password, verbose=verbose)
    if not auth_result:
        sys.exit(1)
    
    token = auth_result['tokens']['access_token']
    
    if verbose:
        print()
        print("📤 Starting course import...")
        print()
    
    # Import course
    importer = LearnHouseImporter(args.url, token, args.org_id, verbose=verbose)
    success = importer.import_course(course_data)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ PUBLISH COMPLETE!")
        print("=" * 60)
        print("Course has been validated, images downloaded, and imported successfully!")
        if verbose:
            print(f"\n📊 Summary:")
            print(f"   ✓ Validation: Passed")
            if not args.skip_images:
                print(f"   ✓ Images: Downloaded")
            print(f"   ✓ Import: Completed")
    else:
        print("\n❌ Course import failed!", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='LearnHouse Course Generator & Importer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  validate        Validate course data JSON file against schema
  validate-org    Validate organization data JSON file against schema
  download-images Download images from course data to local directory
  import          Import course data into LearnHouse platform
  import-org      Import/update organization data into LearnHouse platform
  publish         Complete workflow: validate, download images, and import

Examples:
  %(prog)s validate course_data.json --verbose
  %(prog)s validate-org organisation.json --verbose
  %(prog)s download-images course_data.json --output-dir images
  %(prog)s import course_data.json --url http://localhost:1338 --email admin@school.dev --password admin123
  %(prog)s import-org organisation.json --url http://localhost:1338 --email admin@school.dev --password admin123
  %(prog)s publish course_data.json --url http://localhost:1338 --email admin@school.dev --password admin123
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands', metavar='COMMAND')
    subparsers.required = True
    
    # Validate command
    parser_validate = subparsers.add_parser('validate', help='Validate course data JSON file against schema')
    parser_validate.add_argument(
        'file',
        help='Path to course data JSON file'
    )
    parser_validate.add_argument(
        '--schema',
        help='Path to custom schema file (default: course-schema.json in same directory)',
        default=None
    )
    parser_validate.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation information'
    )
    parser_validate.set_defaults(func=cmd_validate)
    
    # Validate organization command
    parser_validate_org = subparsers.add_parser('validate-org', help='Validate organization data JSON file against schema')
    parser_validate_org.add_argument(
        'file',
        help='Path to organization data JSON file'
    )
    parser_validate_org.add_argument(
        '--schema',
        help='Path to custom schema file (default: organisation-schema.json in same directory)',
        default=None
    )
    parser_validate_org.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation information'
    )
    parser_validate_org.set_defaults(func=cmd_validate_org)
    
    # Import command
    parser_import = subparsers.add_parser('import', help='Import course data into LearnHouse platform')
    parser_import.add_argument(
        'file',
        help='Path to course data JSON file'
    )
    parser_import.add_argument(
        '--url',
        default='http://localhost:1338',
        help='LearnHouse API URL (default: http://localhost:1338)'
    )
    parser_import.add_argument(
        '--email',
        required=True,
        help='Admin email for authentication'
    )
    parser_import.add_argument(
        '--password',
        required=True,
        help='Admin password for authentication'
    )
    parser_import.add_argument(
        '--org-id',
        type=int,
        default=1,
        help='Organization ID (default: 1)'
    )
    parser_import.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip JSON schema validation (not recommended)'
    )
    parser_import.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed verbose output'
    )
    parser_import.set_defaults(func=cmd_import)
    
    # Download images command
    parser_download = subparsers.add_parser('download-images', help='Download images from course data to local directory')
    parser_download.add_argument(
        'file',
        help='Path to course data JSON file'
    )
    parser_download.add_argument(
        '--output-dir', '-o',
        default='images',
        help='Output directory for downloaded images (default: images/)'
    )
    parser_download.add_argument(
        '--force', '-f',
        action='store_true',
        help='Re-download existing images'
    )
    parser_download.add_argument(
        '--mapping-file',
        default='image_mapping.json',
        help='Output file for URL to local file mapping (default: image_mapping.json)'
    )
    parser_download.set_defaults(func=cmd_download_images)
    
    # Import organization command
    parser_import_org = subparsers.add_parser('import-org', help='Import/update organization data into LearnHouse platform')
    parser_import_org.add_argument(
        'file',
        help='Path to organization data JSON file'
    )
    parser_import_org.add_argument(
        '--url',
        default='http://localhost:1338',
        help='LearnHouse API URL (default: http://localhost:1338)'
    )
    parser_import_org.add_argument(
        '--email',
        required=True,
        help='Admin email for authentication'
    )
    parser_import_org.add_argument(
        '--password',
        required=True,
        help='Admin password for authentication'
    )
    parser_import_org.add_argument(
        '--org-id',
        type=int,
        default=None,
        help='Target organization ID (default: auto-detect by slug or use 1)'
    )
    parser_import_org.add_argument(
        '--schema',
        help='Path to custom schema file (default: organisation-schema.json in same directory)',
        default=None
    )
    parser_import_org.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip JSON schema validation (not recommended)'
    )
    parser_import_org.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed verbose output'
    )
    parser_import_org.set_defaults(func=cmd_import_org)
    
    # Publish command
    parser_publish = subparsers.add_parser('publish', help='Complete workflow: validate, download images, and import course data')
    parser_publish.add_argument(
        'file',
        help='Path to course data JSON file'
    )
    parser_publish.add_argument(
        '--url',
        default='http://localhost:1338',
        help='LearnHouse API URL (default: http://localhost:1338)'
    )
    parser_publish.add_argument(
        '--email',
        required=True,
        help='Admin email for authentication'
    )
    parser_publish.add_argument(
        '--password',
        required=True,
        help='Admin password for authentication'
    )
    parser_publish.add_argument(
        '--org-id',
        type=int,
        default=1,
        help='Organization ID (default: 1)'
    )
    parser_publish.add_argument(
        '--schema',
        help='Path to custom schema file (default: course-schema.json in same directory)',
        default=None
    )
    parser_publish.add_argument(
        '--images-dir',
        help='Directory to download images (default: data/images/)',
        default=None
    )
    parser_publish.add_argument(
        '--mapping-file',
        help='Output file for URL to local file mapping (default: data/image_mapping.json)',
        default=None
    )
    parser_publish.add_argument(
        '--skip-images',
        action='store_true',
        help='Skip downloading images'
    )
    parser_publish.add_argument(
        '--force', '-f',
        action='store_true',
        help='Re-download existing images'
    )
    parser_publish.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed verbose output'
    )
    parser_publish.set_defaults(func=cmd_publish)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

