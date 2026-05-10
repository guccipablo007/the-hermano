import json
import re
import shlex
import subprocess
import time
from pathlib import Path
ROUTER='/root/.hermes/scripts/hermes_router_execute.py'
DOC_BUILDER='/root/.hermes/scripts/hermes_document_builder.py'
def _safe_slug(text):
    text=(text or 'document').lower(); text=re.sub(r'[^a-z0-9]+','_',text).strip('_'); return text[:60] or 'document'
def _run(cmd, timeout=300):
    proc=subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout); return proc.returncode, proc.stdout, proc.stderr
def _make_markdown(title, content):
    title=title or 'Document'; content=content or ''
    if content.lstrip().startswith('#'): return content.strip()+'\n'
    return f'# {title}\n\n{content.strip()}\n'
def _handle_document_output(params):
    title=params.get('title') or 'Hermes Document'
    content=params.get('content') or ''
    description=params.get('description') or ''
    output_format=(params.get('output_format') or 'pdf').lower().strip()
    output_format={'markdown':'md','word':'docx'}.get(output_format, output_format)
    expect_text=params.get('expect_text') or title
    deliver=(params.get('deliver') or 'telegram').lower().strip()
    output_path=params.get('output_path') or ''
    if output_format not in ['pdf','docx','md','html','pptx','rich_pdf_picture','rich_docx_picture']:
        return 'NOT VERIFIED\nREASON=UNSUPPORTED_OUTPUT_FORMAT\nSUPPORTED=pdf,docx,md,html,pptx,rich_pdf_picture,rich_docx_picture'
    slug=_safe_slug(title)
    if output_format in ['rich_pdf_picture','rich_docx_picture']:
        fmt_mode='rich_pdf_picture_file' if output_format=='rich_pdf_picture' else 'rich_docx_picture_file'
        if not output_path:
            ext='pdf' if output_format=='rich_pdf_picture' else 'docx'
            output_path=f'/root/.hermes/file_outputs/{slug}.{ext}'
        topic=params.get('topic') or title
        age=params.get('age') or 'kids'
        min_media=int(params.get('min_media') or 1)
        cmd=(f'{shlex.quote(ROUTER)} {fmt_mode} --output {shlex.quote(output_path)} --title {shlex.quote(title)} --topic {shlex.quote(topic)} --age {shlex.quote(age)} --min-media {min_media}')
        if deliver=='no': cmd+=' --no-deliver-telegram'
        rc,out,err=_run(cmd)
        if rc!=0: return 'NOT VERIFIED\nFORMAT=' + output_format + '\nSTDOUT=' + out + '\nSTDERR=' + err
        return out.strip()

    if output_format=='html':
        if not output_path: output_path=f'/root/.hermes/newcoin_outputs/{slug}.html'
        desc=description or content or f'Create an HTML page titled {title}.'
        cmd=(f'{shlex.quote(ROUTER)} html_file --output {shlex.quote(output_path)} --description {shlex.quote(desc)} --expect-text {shlex.quote(expect_text)}')
        if deliver=='no': cmd+=' --no-deliver-telegram'
        rc,out,err=_run(cmd)
        if rc!=0: return f'NOT VERIFIED\nFORMAT=html\nSTDOUT={out}\nSTDERR={err}'
        return out.strip()
    if not output_path: output_path=f'/root/.hermes/file_outputs/{slug}.{output_format}'
    tmp_dir=Path('/root/.hermes/telegram_outputs/router_content'); tmp_dir.mkdir(parents=True, exist_ok=True)
    content_file=tmp_dir/f'{slug}_{int(time.time())}.md'; content_file.write_text(_make_markdown(title, content), encoding='utf-8')
    cmd=(f'/usr/bin/python3 {shlex.quote(DOC_BUILDER)} --format {shlex.quote(output_format)} --output {shlex.quote(output_path)} --title {shlex.quote(title)} --description {shlex.quote(description or ("Create document: "+title))} --expect-text {shlex.quote(expect_text)} --content-file {shlex.quote(str(content_file))}')
    if deliver=='no': cmd+=' --no-deliver-telegram'
    else: cmd+=' --deliver-telegram'
    rc,out,err=_run(cmd)
    if rc!=0: return f'NOT VERIFIED\nFORMAT={output_format}\nOUTPUT_PATH={output_path}\nSTDOUT={out}\nSTDERR={err}'
    return out.strip()
def register(ctx):
    schema={'name':'document-output-router','description':'Create verified PDF, DOCX, Markdown, or HTML files and optionally deliver them to Telegram.','parameters':{'type':'object','properties':{'title':{'type':'string','description':'Document title'},'content':{'type':'string','description':'Markdown or plain content to include'},'description':{'type':'string','description':'Optional task description'},'output_format':{'type':'string','enum':['pdf','docx','rich_pdf_picture','rich_docx_picture','pptx','md','markdown','html'],'description':'Output format'},'output_path':{'type':'string','description':'Optional exact output path'},'expect_text':{'type':'string','description':'Text expected in the output'},'deliver':{'type':'string','enum':['telegram','no'],'description':'Whether to deliver to Telegram'}},'required':['title','output_format']}}
    schema2=dict(schema); schema2['name']='document_output_router'
    ctx.register_tool('document-output-router', schema, _handle_document_output)
    ctx.register_tool('document_output_router', schema2, _handle_document_output)
