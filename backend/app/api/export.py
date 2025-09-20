from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter(prefix="", tags=["export"])


class ExportRequest(BaseModel):
    doc_id: str
    analysis: dict


@router.post("/export")
async def export_report(payload: ExportRequest):
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Export request received for doc_id: {payload.doc_id}")
    
    pdf_io = BytesIO()
    
    try:
        # Try WeasyPrint first (better formatting), but skip on Windows due to GTK dependency issues
        import platform
        use_weasyprint = platform.system() != 'Windows'
        
        if use_weasyprint:
            try:
                from weasyprint import HTML  # type: ignore
                logger.info("Using WeasyPrint for PDF generation")
                
                # Format the analysis data nicely
                analysis_text = json.dumps(payload.analysis, indent=2)
                
                html = f"""
                <!DOCTYPE html>
                <html>
                  <head>
                    <meta charset="utf-8">
                    <style>
                      body {{ 
                        font-family: 'Inter', system-ui, Arial, sans-serif; 
                        margin: 40px; 
                        line-height: 1.6;
                        color: #333;
                      }}
                      h1 {{ 
                        color: #4f46e5; 
                        border-bottom: 2px solid #e5e7eb; 
                        padding-bottom: 10px;
                      }}
                      pre {{ 
                        background: #f9fafb; 
                        padding: 20px; 
                        border-radius: 8px; 
                        border: 1px solid #e5e7eb;
                        white-space: pre-wrap; 
                        font-size: 12px;
                        overflow-x: auto;
                      }}
                    </style>
                  </head>
                  <body>
                    <h1>LegalLens Report</h1>
                    <p><strong>Document ID:</strong> {payload.doc_id}</p>
                    <p><strong>Generated:</strong> {json.dumps(payload.analysis.get('timestamp', 'Unknown'), indent=2)}</p>
                    <h2>Analysis Results</h2>
                    <pre>{analysis_text}</pre>
                  </body>
                </html>
                """
                HTML(string=html).write_pdf(pdf_io)
                logger.info("WeasyPrint PDF generation successful")
                
            except Exception as weasy_error:
                logger.warning(f"WeasyPrint failed: {weasy_error}, falling back to ReportLab")
                use_weasyprint = False
        
        if not use_weasyprint:
            # Use ReportLab (more reliable on Windows)
            from reportlab.lib.pagesizes import A4  # type: ignore
            from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted  # type: ignore
            from reportlab.lib.units import inch  # type: ignore
            from reportlab.lib import colors  # type: ignore
            
            logger.info("Using ReportLab for PDF generation")
            
            # Create a more structured PDF with ReportLab
            doc = SimpleDocTemplate(pdf_io, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("LegalLens Report", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Document ID
            doc_id_para = Paragraph(f"<b>Document ID:</b> {payload.doc_id}", styles['Normal'])
            story.append(doc_id_para)
            story.append(Spacer(1, 20))
            
            # Analysis content
            analysis_text = json.dumps(payload.analysis, indent=2)
            
            # Add sections for better readability
            if 'answer' in payload.analysis:
                answer_para = Paragraph(f"<b>Answer:</b><br/>{payload.analysis['answer']}", styles['Normal'])
                story.append(answer_para)
                story.append(Spacer(1, 15))
            
            if 'risk' in payload.analysis:
                risk_para = Paragraph(f"<b>Risk Assessment:</b><br/>Level: {payload.analysis['risk'].get('level', 'Unknown')}<br/>Score: {payload.analysis['risk'].get('score', 'Unknown')}", styles['Normal'])
                story.append(risk_para)
                story.append(Spacer(1, 15))
            
            if 'confidence' in payload.analysis:
                conf_para = Paragraph(f"<b>Confidence:</b> {payload.analysis['confidence']}", styles['Normal'])
                story.append(conf_para)
                story.append(Spacer(1, 15))
            
            # Full analysis as preformatted text
            # full_analysis = Preformatted(analysis_text, styles['Code'])
            # story.append(Paragraph("<b>Full Analysis:</b>", styles['Heading2']))
            # story.append(full_analysis)
            
            doc.build(story)
            logger.info("ReportLab PDF generation successful")
            
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        # Return a simple error response
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    pdf_io.seek(0)
    logger.info("PDF export completed successfully")
    
    return StreamingResponse(
        pdf_io, 
        media_type='application/pdf', 
        headers={
            'Content-Disposition': f"attachment; filename=legal-lens-report-{payload.doc_id}.pdf"
        }
    )


