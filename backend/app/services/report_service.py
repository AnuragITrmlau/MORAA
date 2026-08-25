"""Report generation service for creating PDF reports."""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.config import settings
from app.models.report import Report
from app.models.analysis import Analysis
from app.repositories.base import BaseRepository
from app.schemas.report import ReportResponse, ReportConfigRequest
from app.utils.logger import logger


class ReportService:
    """Report generation and management service."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = BaseRepository(Report, db)
        self.analysis_repo = BaseRepository(Analysis, db)

    async def generate_report(
        self,
        config: ReportConfigRequest,
        user_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
    ) -> ReportResponse:
        """Generate a PDF/markdown report."""
        report_id = str(uuid.uuid4())
        filename = f"MORAA_GemVision_Report_{config.type}_{report_id[:8]}.pdf"

        # Ensure report directory exists
        report_dir = settings.REPORT_PATH
        report_dir.mkdir(parents=True, exist_ok=True)

        file_path = report_dir / filename

        # Generate PDF content
        if config.format == "pdf":
            await self._generate_pdf_report(
                file_path=str(file_path),
                report_type=config.type,
                include_charts=config.includeCharts,
                analysis_id=analysis_id,
            )

        # Get file size
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        # Save to database
        report = self.repo.create(
            id=report_id,
            analysis_id=analysis_id,
            user_id=user_id,
            report_type=config.type,
            format=config.format,
            filename=filename,
            file_path=str(file_path),
            file_size=file_size,
            page_count=1,
            include_charts=config.includeCharts,
        )

        logger.bind(category="report").info(
            f"Report generated: {filename} ({config.type})"
        )

        return ReportResponse(
            id=report.id,
            filename=report.filename,
            size=report.file_size or 0,
            pages=report.page_count or 0,
            generatedAt=report.generated_at,
            type=report.report_type,
            format=report.format,
        )

    async def _generate_pdf_report(
        self,
        file_path: str,
        report_type: str,
        include_charts: bool = True,
        analysis_id: Optional[str] = None,
    ) -> None:
        """Generate a styled PDF report using ReportLab."""
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor("#1a1a2e"),
        )
        story.append(Paragraph("MORAA GemVision Analysis Report", title_style))
        story.append(Spacer(1, 12))

        # Report metadata
        meta_style = ParagraphStyle(
            "Meta",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
        )
        story.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
                meta_style,
            )
        )
        story.append(
            Paragraph(f"Report Type: {report_type.title()}", meta_style)
        )
        story.append(Spacer(1, 24))

        # Analysis data
        if analysis_id:
            analysis = self.analysis_repo.get(analysis_id)
            if analysis:
                story.append(
                    Paragraph("Analysis Results", styles["Heading2"])
                )
                story.append(Spacer(1, 12))

                data = [
                    ["Property", "Value"],
                    ["Material", analysis.material or "N/A"],
                    ["Gold Purity", analysis.gold_purity or "N/A"],
                    ["Weight", f"{analysis.weight}g" if analysis.weight else "N/A"],
                    ["Category", analysis.category or "N/A"],
                    [
                        "Estimated Price",
                        f"${analysis.estimated_price:,.2f}" if analysis.estimated_price else "N/A",
                    ],
                    [
                        "Confidence",
                        f"{analysis.confidence:.1%}" if analysis.confidence else "N/A",
                    ],
                    ["Style", analysis.style or "N/A"],
                    ["Era", analysis.era or "N/A"],
                    ["Condition", analysis.condition or "N/A"],
                ]

                table = Table(data, colWidths=[200, 300])
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 11),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#dee2e6")),
                            ("FONTSIZE", (0, 1), (-1, -1), 10),
                            ("TOPPADDING", (0, 1), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                        ]
                    )
                )
                story.append(table)

                # Summary
                if analysis.summary:
                    story.append(Spacer(1, 20))
                    story.append(
                        Paragraph("Summary", styles["Heading2"])
                    )
                    story.append(Spacer(1, 8))
                    story.append(
                        Paragraph(analysis.summary, styles["Normal"])
                    )

        # Build PDF
        doc.build(story)

    def get_report(self, report_id: str) -> Optional[Report]:
        """Get report by ID."""
        return self.repo.get(report_id)

    def get_report_file_path(self, report_id: str) -> Optional[str]:
        """Get the file path for a report."""
        report = self.repo.get(report_id)
        if not report:
            return None
        return report.file_path
