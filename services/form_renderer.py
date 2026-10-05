"""
Form Renderer — Exact high-fidelity visual recreation of the official
'સભ્ય નોંધણી ફોર્મ' of 'શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.'

Matches the updated official physical membership form with improved Gujarati orthography:
  - Page: A4 portrait aspect ratio (724 x 1024 coordinate system)
  - Double blue border (outer thin line, spacing, inner crisp line)
  - Lord Parshuram logo on rock holding axe at top-left
  - Blue rounded top banner 'સભ્ય નોંધણી ફોર્મ'
  - Organization title: 'શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.'
  - Organization address: 'એફ.એફ-૧૧૪, પહેલો માળ, શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર.'
  - Form Meta: ફોર્મ ક્રમાંક : & તારીખ :
  - Section 1 (૧ થી ૬) — ૧. સભ્યની વ્યક્તિગત માહિતી:
      (૧) પૂર્ણ નામ (અટક પહેલાં લખવી)
      (૨) પત્રવ્યવહારનું સરનામું (રહેઠાણનું સરનામું) [2 lines]
      (૩) ગામનું સરનામું [2 lines]
      (૪) ઈ-મેલ આઈડી
      (૫) શિક્ષણ
      (૬) મોબાઇલ નંબર & ફોન નંબર
  - Section 2 (૭ થી ૯) — ૨. વ્યવસાય / રોજગારની માહિતી:
      (૭) ધંધો / વ્યવસાય
      (૮) ધંધા / વ્યવસાયનું સરનામું [2 lines]
      (૯) બ્લડ ગ્રુપ
  - Section 3 (૧૦ થી ૧૧) — ૩. સમાજની માહિતી:
      (૧૦) સમાજ
      (૧૧) સભ્ય ફી: ____ મોકલેલ છે.    ફોર્મ ભરનારની સહી: ____
  - Section 4 (૪. પરિવારની માહિતી):
      10-row, 8-column official family members table with blue gridlines:
      (ક્રમ, નામ, સંબંધ, ઉંમર, અભ્યાસ, બ્લડ ગ્રુપ, વ્યવસાય, સંપર્ક નંબર)
      Rows numbered in correct Gujarati numerals: ૧, ૨, ૩, ૪, ૫, ૬, ૭, ૮, ૯, ૧૦
"""

from __future__ import annotations

import os
from typing import Any

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontDatabase,
    QPainterPath, QPixmap,
)

from app.config import (
    GUJARATI_FONT_REGULAR, GUJARATI_FONT_BOLD,
    LOGO_PATH,
)

# ── Color Palette (exact matching to physical form) ───────────────────────────
COLOR_BLUE = QColor('#1B2F8A')
COLOR_BLUE_DARK = QColor('#142268')
COLOR_WHITE = QColor('#FFFFFF')
COLOR_TEXT_VALUE = QColor('#101828')

# Reference coordinate grid
CANVAS_W = 724.0
CANVAS_H = 1024.0

# ── Outer / Inner Border Coordinates ──────────────────────────────────────────
OUTER_X = 13.0
OUTER_Y = 13.0
OUTER_W = 698.0
OUTER_H = 997.0

INNER_X = 22.0
INNER_Y = 22.0
INNER_W = 679.0
INNER_H = 979.0
INNER_RIGHT = INNER_X + INNER_W   # 701.0
INNER_BOTTOM = INNER_Y + INNER_H  # 1001.0

# ── Table Layout Coordinates ──────────────────────────────────────────────────
# Horizontal dividing lines:
DIVIDER_0_Y     = 136.0   # Divider below Form No & Date
DIVIDER_1_Y     = 368.0   # Divider below Section 1 (Personal Info with Education & Village Address)
DIVIDER_2_Y     = 516.0   # Divider below Section 2 (Business & Blood Group)
DIVIDER_3_Y     = 608.0   # Divider below Section 3 (Samaj & Fee / Signature)
TABLE_TOP_Y     = 638.0   # Top of the family table headers
TABLE_HDR_BOT_Y = 666.0   # Bottom of family table header row (height = 28)
TABLE_ROW_H     = 33.5    # (1001 - 666) / 10 rows = 33.5 px per row
TABLE_BOT_Y     = 1001.0  # Bottom of table (connects to inner bottom border)

# Vertical column dividing lines (x coords for 8 columns):
COL_X = [
    22.0,   # Left border
    55.0,   # Col 0 (ક્રમ) right
    220.0,  # Col 1 (નામ) right
    285.0,  # Col 2 (સંબંધ) right
    330.0,  # Col 3 (ઉંમર) right
    425.0,  # Col 4 (અભ્યાસ) right
    495.0,  # Col 5 (બ્લડ ગ્રુપ) right
    595.0,  # Col 6 (વ્યવસાય) right
    701.0,  # Col 7 (સંપર્ક નંબર) right
]

# Official 8 Column Headers with corrected Gujarati spelling (ક્રમ not કમ, સંબંધ not સંબંઘ)
COL_HEADERS = [
    'ક્રમ', 'નામ', 'સંબંધ', 'ઉંમર',
    'અભ્યાસ', 'બ્લડ ગ્રુપ', 'વ્યવસાય', 'સંપર્ક નંબર',
]

# Pre-printed Row Serials in accurate Gujarati numerals (૧ થી ૧૦, with no skipped digits or English numbers)
GUJARATI_ROW_NUMERALS = ['૧', '૨', '૩', '૪', '૫', '૬', '૭', '૮', '૯', '૧૦']


def ensure_gujarati_fonts_loaded() -> str:
    """Ensure Noto Sans Gujarati fonts are loaded into Qt's QFontDatabase."""
    if os.path.exists(GUJARATI_FONT_REGULAR):
        QFontDatabase.addApplicationFont(GUJARATI_FONT_REGULAR)
    if os.path.exists(GUJARATI_FONT_BOLD):
        QFontDatabase.addApplicationFont(GUJARATI_FONT_BOLD)
    return 'Noto Sans Gujarati'


class FormRenderer:
    """Renders the official membership form on any QPainter device."""

    @staticmethod
    def draw_form(
        painter: QPainter,
        form_data: dict[str, Any] | None = None,
        width: float = CANVAS_W,
        height: float = CANVAS_H,
        draw_background: bool = True,
        draw_labels_and_lines: bool = True,
        draw_values: bool = True,
    ) -> None:
        """
        Draw the form onto the target painter.
        Supports arbitrary scaling by translating and scaling to (width, height).
        """
        data = form_data or {}
        font_family = ensure_gujarati_fonts_loaded()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Scale coordinate system to match target width / height
        scale_x = width / CANVAS_W
        scale_y = height / CANVAS_H
        painter.scale(scale_x, scale_y)

        # 1. Background fill
        if draw_background:
            painter.fillRect(QRectF(0, 0, CANVAS_W, CANVAS_H), COLOR_WHITE)

        if draw_labels_and_lines:
            FormRenderer._draw_borders(painter)
            FormRenderer._draw_header(painter, font_family)
            FormRenderer._draw_section1(painter, font_family)
            FormRenderer._draw_section2(painter, font_family)
            FormRenderer._draw_section3(painter, font_family)
            FormRenderer._draw_section4(painter, font_family)

        if draw_values:
            FormRenderer._draw_field_values(painter, data, font_family)

        painter.restore()

    # ── Borders ───────────────────────────────────────────────────────────────
    @staticmethod
    def _draw_borders(p: QPainter) -> None:
        # Outer thin border
        pen_outer = QPen(COLOR_BLUE, 1.2, Qt.PenStyle.SolidLine)
        p.setPen(pen_outer)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(QRectF(OUTER_X, OUTER_Y, OUTER_W, OUTER_H))

        # Inner border
        pen_inner = QPen(COLOR_BLUE, 1.6, Qt.PenStyle.SolidLine)
        p.setPen(pen_inner)
        p.drawRect(QRectF(INNER_X, INNER_Y, INNER_W, INNER_H))

    @staticmethod
    def _draw_ribbon_banner(
        p: QPainter, text: str, font_family: str,
        x: float, y: float, w: float, h: float, r: float = 8.0,
        font_size: int = 13,
    ) -> None:
        """Draw a rounded dark blue banner badge with centered white text."""
        banner_path = QPainterPath()
        banner_path.addRoundedRect(QRectF(x, y, w, h), r, r)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(COLOR_BLUE)
        p.drawPath(banner_path)

        p.setPen(COLOR_WHITE)
        font = QFont(font_family)
        font.setPixelSize(font_size)
        font.setBold(True)
        p.setFont(font)
        p.drawText(QRectF(x, y + 1, w, h - 1), Qt.AlignmentFlag.AlignCenter, text)

    # ── Header ────────────────────────────────────────────────────────────────
    @staticmethod
    def _draw_header(p: QPainter, font_family: str) -> None:
        # Top banner: "સભ્ય નોંધણી ફોર્મ" hanging from inner top border
        banner_path = QPainterPath()
        bx, by, bw, bh, br = 232.0, INNER_Y, 260.0, 34.0, 12.0
        banner_path.moveTo(bx, by)
        banner_path.lineTo(bx + bw, by)
        banner_path.lineTo(bx + bw, by + bh - br)
        banner_path.arcTo(bx + bw - 2 * br, by + bh - 2 * br, 2 * br, 2 * br, 0, -90)
        banner_path.lineTo(bx + br, by + bh)
        banner_path.arcTo(bx, by + bh - 2 * br, 2 * br, 2 * br, 270, -90)
        banner_path.closeSubpath()

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(COLOR_BLUE)
        p.drawPath(banner_path)

        p.setPen(COLOR_WHITE)
        banner_font = QFont(font_family)
        banner_font.setPixelSize(17)
        banner_font.setBold(True)
        p.setFont(banner_font)
        p.drawText(QRectF(bx, by + 2, bw, bh - 2), Qt.AlignmentFlag.AlignCenter, 'સભ્ય નોંધણી ફોર્મ')

        # Lord Parshuram Logo (top-left)
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH)
            p.drawPixmap(
                QRectF(46.0, 24.0, 75.0, 82.0),
                pix,
                QRectF(0, 0, pix.width(), pix.height()),
            )

        # Organization Title
        title_font = QFont(font_family)
        title_font.setPixelSize(21)
        title_font.setBold(True)
        p.setFont(title_font)
        p.setPen(COLOR_BLUE)
        p.drawText(QRectF(140.0, 58.0, 545.0, 28.0), Qt.AlignmentFlag.AlignCenter, 'શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.')

        # Organization Address — authentic matching with corrected Gujarati spelling
        addr_font = QFont(font_family)
        addr_font.setPixelSize(10)
        addr_font.setBold(True)
        p.setFont(addr_font)
        p.drawText(
            QRectF(140.0, 88.0, 545.0, 18.0),
            Qt.AlignmentFlag.AlignCenter,
            'એફ.એફ-૧૧૪, પહેલો માળ, શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર.',
        )

        # Meta line: ફોર્મ ક્રમાંક : & તારીખ :
        pen_line = QPen(COLOR_BLUE, 1.1, Qt.PenStyle.SolidLine)
        p.setPen(pen_line)
        label_font = QFont(font_family)
        label_font.setPixelSize(12)
        label_font.setBold(True)
        p.setFont(label_font)

        p.drawText(QRectF(33, 112, 88, 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'ફોર્મ ક્રમાંક :')
        p.drawLine(QPointF(124, 128), QPointF(280, 128))

        p.drawText(QRectF(485, 112, 55, 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'તારીખ :')
        p.drawLine(QPointF(545, 128), QPointF(688, 128))

        # Divider line below meta bar
        pen_divider = QPen(COLOR_BLUE, 1.3, Qt.PenStyle.SolidLine)
        p.setPen(pen_divider)
        p.drawLine(QPointF(INNER_X, DIVIDER_0_Y), QPointF(INNER_RIGHT, DIVIDER_0_Y))

    @staticmethod
    def _draw_badge(p: QPainter, text: str, font_family: str, cx: float, cy: float, r: float = 8.5) -> None:
        """Draw a solid dark blue circular badge with centered white bold numeral."""
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(COLOR_BLUE)
        p.drawEllipse(QPointF(cx, cy), r, r)
        p.setPen(COLOR_WHITE)
        b_font = QFont(font_family)
        b_font.setPixelSize(9 if len(text) > 1 else 10)
        b_font.setBold(True)
        p.setFont(b_font)
        p.drawText(QRectF(cx - r, cy - r, 2 * r, 2 * r), Qt.AlignmentFlag.AlignCenter, text)
        p.restore()

    # ── Section 1: સભ્યની વ્યક્તિગત માહિતી ─────────────────────────────────
    @staticmethod
    def _draw_section1(p: QPainter, font_family: str) -> None:
        # Banner: ૧. સભ્યની વ્યક્તિગત માહિતી
        FormRenderer._draw_ribbon_banner(p, '૧. સભ્યની વ્યક્તિગત માહિતી', font_family, 236.0, DIVIDER_0_Y, 252.0, 26.0, r=8.0, font_size=13)

        pen_line = QPen(COLOR_BLUE, 1.1, Qt.PenStyle.SolidLine)
        p.setPen(pen_line)

        label_font = QFont(font_family)
        label_font.setPixelSize(12)
        label_font.setBold(True)
        p.setFont(label_font)
        p.setPen(COLOR_BLUE)

        # Line 1: Badge ૧ + પૂર્ણ નામ (અટક પહેલાં લખવી) :
        FormRenderer._draw_badge(p, '૧', font_family, 43.0, 180.0, 8.5)
        p.drawText(QRectF(56, 170, 215, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'પૂર્ણ નામ (અટક પહેલાં લખવી) :')
        p.drawLine(QPointF(272, 188), QPointF(688, 188))

        # Line 2: Badge ૨ + પત્રવ્યવહારનું સરનામું (રહેઠાણનું સરનામું) :
        FormRenderer._draw_badge(p, '૨', font_family, 43.0, 204.0, 8.5)
        p.drawText(QRectF(56, 194, 275, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'પત્રવ્યવહારનું સરનામું (રહેઠાણનું સરનામું) :')
        p.drawLine(QPointF(332, 212), QPointF(688, 212))

        # Line 3: Correspondence Address continuation line
        p.drawLine(QPointF(56, 234), QPointF(688, 234))

        # Line 4: Badge ૩ + ગામનું સરનામું :
        FormRenderer._draw_badge(p, '૩', font_family, 43.0, 251.0, 8.5)
        p.drawText(QRectF(56, 241, 115, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'ગામનું સરનામું :')
        p.drawLine(QPointF(172, 259), QPointF(688, 259))

        # Line 5: Village Address continuation line
        p.drawLine(QPointF(56, 281), QPointF(688, 281))

        # Line 6: Badge ૪ + ઈ-મેલ આઈડી :
        FormRenderer._draw_badge(p, '૪', font_family, 43.0, 298.0, 8.5)
        p.drawText(QRectF(56, 288, 90, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'ઈ-મેલ આઈડી :')
        p.drawLine(QPointF(148, 306), QPointF(688, 306))

        # Line 7: Badge ૫ + શિક્ષણ :
        FormRenderer._draw_badge(p, '૫', font_family, 43.0, 321.0, 8.5)
        p.drawText(QRectF(56, 311, 65, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'શિક્ષણ :')
        p.drawLine(QPointF(122, 329), QPointF(688, 329))

        # Line 8: Badge ૬ + મોબાઇલ નંબર : & ફોન નંબર :
        FormRenderer._draw_badge(p, '૬', font_family, 43.0, 345.0, 8.5)
        p.drawText(QRectF(56, 335, 96, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'મોબાઇલ નંબર :')
        p.drawLine(QPointF(154, 353), QPointF(420, 353))

        p.drawText(QRectF(432, 335, 70, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'ફોન નંબર :')
        p.drawLine(QPointF(504, 353), QPointF(688, 353))

        # Divider line below Section 1
        pen_divider = QPen(COLOR_BLUE, 1.3, Qt.PenStyle.SolidLine)
        p.setPen(pen_divider)
        p.drawLine(QPointF(INNER_X, DIVIDER_1_Y), QPointF(INNER_RIGHT, DIVIDER_1_Y))

    # ── Section 2: વ્યવસાય / રોજગારની માહિતી ───────────────────────────────
    @staticmethod
    def _draw_section2(p: QPainter, font_family: str) -> None:
        # Banner: ૨. વ્યવસાય / રોજગારની માહિતી
        FormRenderer._draw_ribbon_banner(p, '૨. વ્યવસાય / રોજગારની માહિતી', font_family, 226.0, DIVIDER_1_Y, 272.0, 26.0, r=8.0, font_size=13)

        pen_line = QPen(COLOR_BLUE, 1.1, Qt.PenStyle.SolidLine)
        p.setPen(pen_line)

        label_font = QFont(font_family)
        label_font.setPixelSize(12)
        label_font.setBold(True)
        p.setFont(label_font)
        p.setPen(COLOR_BLUE)

        # Line 1: Badge ૭ + ધંધો / વ્યવસાય :
        FormRenderer._draw_badge(p, '૭', font_family, 43.0, 412.0, 8.5)
        p.drawText(QRectF(56, 402, 125, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'ધંધો / વ્યવસાય :')
        p.drawLine(QPointF(182, 420), QPointF(688, 420))

        # Line 2: Badge ૮ + ધંધા / વ્યવસાયનું સરનામું :
        FormRenderer._draw_badge(p, '૮', font_family, 43.0, 438.0, 8.5)
        p.drawText(QRectF(56, 428, 185, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'ધંધા / વ્યવસાયનું સરનામું :')
        p.drawLine(QPointF(242, 446), QPointF(688, 446))

        # Line 3: Business Address continuation line
        p.drawLine(QPointF(56, 469), QPointF(688, 469))

        # Line 4: Badge ૯ + બ્લડ ગ્રુપ :
        FormRenderer._draw_badge(p, '૯', font_family, 43.0, 494.0, 8.5)
        p.drawText(QRectF(56, 484, 90, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'બ્લડ ગ્રુપ :')
        p.drawLine(QPointF(148, 502), QPointF(465, 502))

        # Divider line below Section 2
        pen_divider = QPen(COLOR_BLUE, 1.3, Qt.PenStyle.SolidLine)
        p.setPen(pen_divider)
        p.drawLine(QPointF(INNER_X, DIVIDER_2_Y), QPointF(INNER_RIGHT, DIVIDER_2_Y))

    # ── Section 3: સમાજની માહિતી ───────────────────────────────────────────
    @staticmethod
    def _draw_section3(p: QPainter, font_family: str) -> None:
        # Banner: ૩. સમાજની માહિતી
        FormRenderer._draw_ribbon_banner(p, '૩. સમાજની માહિતી', font_family, 247.0, DIVIDER_2_Y, 230.0, 26.0, r=8.0, font_size=13)

        pen_line = QPen(COLOR_BLUE, 1.1, Qt.PenStyle.SolidLine)
        p.setPen(pen_line)

        label_font = QFont(font_family)
        label_font.setPixelSize(12)
        label_font.setBold(True)
        p.setFont(label_font)
        p.setPen(COLOR_BLUE)

        # Line 1: Badge ૧૦ + સમાજ :
        FormRenderer._draw_badge(p, '૧૦', font_family, 43.0, 558.0, 9.5)
        p.drawText(QRectF(56, 548, 65, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'સમાજ :')
        p.drawLine(QPointF(122, 566), QPointF(688, 566))

        # Line 2: Badge ૧૧ + સભ્ય ફી : ... મોકલેલ છે.    ફોર્મ ભરનારની સહી :
        FormRenderer._draw_badge(p, '૧૧', font_family, 43.0, 585.0, 9.5)
        p.drawText(QRectF(56, 575, 65, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'સભ્ય ફી :')
        p.drawLine(QPointF(122, 593), QPointF(255, 593))

        p.drawText(QRectF(265, 575, 85, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'મોકલેલ છે.')

        p.drawText(QRectF(380, 575, 145, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'ફોર્મ ભરનારની સહી :')
        p.drawLine(QPointF(528, 593), QPointF(688, 593))

        # Divider line below Section 3
        pen_divider = QPen(COLOR_BLUE, 1.3, Qt.PenStyle.SolidLine)
        p.setPen(pen_divider)
        p.drawLine(QPointF(INNER_X, DIVIDER_3_Y), QPointF(INNER_RIGHT, DIVIDER_3_Y))

    # ── Section 4: પરિવારની માહિતી (Family Information Table) ─────────────
    @staticmethod
    def _draw_section4(p: QPainter, font_family: str) -> None:
        # Banner: ૪. પરિવારની માહિતી
        FormRenderer._draw_ribbon_banner(p, '૪. પરિવારની માહિતી', font_family, 236.0, DIVIDER_3_Y, 252.0, 26.0, r=8.0, font_size=13)

        # Table Horizontal Lines
        pen_grid = QPen(COLOR_BLUE, 1.1, Qt.PenStyle.SolidLine)
        p.setPen(pen_grid)

        # Top border of table
        p.drawLine(QPointF(INNER_X, TABLE_TOP_Y), QPointF(INNER_RIGHT, TABLE_TOP_Y))

        # Bottom border of table header
        p.drawLine(QPointF(INNER_X, TABLE_HDR_BOT_Y), QPointF(INNER_RIGHT, TABLE_HDR_BOT_Y))

        # 10 Data row dividing lines (9 inner row lines)
        for r in range(1, 10):
            ry = TABLE_HDR_BOT_Y + r * TABLE_ROW_H
            p.drawLine(QPointF(INNER_X, ry), QPointF(INNER_RIGHT, ry))

        # Bottom border of table (connects to INNER_BOTTOM)
        p.drawLine(QPointF(INNER_X, TABLE_BOT_Y), QPointF(INNER_RIGHT, TABLE_BOT_Y))

        # Vertical Column Dividing Lines
        for cx in COL_X[1:-1]:
            p.drawLine(QPointF(cx, TABLE_TOP_Y), QPointF(cx, TABLE_BOT_Y))

        # Table Header Labels (Correct Gujarati spelling: ક્રમ, સંબંધ)
        hdr_font = QFont(font_family)
        hdr_font.setPixelSize(11)
        hdr_font.setBold(True)
        p.setFont(hdr_font)
        p.setPen(COLOR_BLUE)
        for i in range(len(COL_HEADERS)):
            rx = COL_X[i]
            rw = COL_X[i + 1] - rx
            rect = QRectF(rx, TABLE_TOP_Y, rw, TABLE_HDR_BOT_Y - TABLE_TOP_Y)
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, COL_HEADERS[i])

        # Pre-printed Row Numbers in Column 0 (ક્રમ) using official Gujarati numerals ૧ થી ૧૦
        num_font = QFont(font_family)
        num_font.setPixelSize(11)
        num_font.setBold(True)
        p.setFont(num_font)
        p.setPen(COLOR_BLUE)
        for r in range(10):
            ry = TABLE_HDR_BOT_Y + r * TABLE_ROW_H
            rect = QRectF(COL_X[0], ry, COL_X[1] - COL_X[0], TABLE_ROW_H)
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, GUJARATI_ROW_NUMERALS[r])

    # ── Field Values Drawing (for Print & PDF) ────────────────────────────────
    @staticmethod
    def _draw_field_values(p: QPainter, data: dict[str, Any], font_family: str) -> None:
        val_font = QFont(font_family)
        val_font.setPixelSize(12)
        p.setFont(val_font)
        p.setPen(COLOR_TEXT_VALUE)

        def draw_val(x: float, y: float, w: float, text: str, align=Qt.AlignmentFlag.AlignLeft):
            if not text:
                return
            rect = QRectF(x, y - 18.0, w, 18.0)
            p.drawText(rect, align | Qt.AlignmentFlag.AlignBottom, str(text).strip())

        # Header Meta: Form No & Date
        draw_val(126, 127, 150, data.get('form_number', ''))
        draw_val(548, 127, 138, data.get('form_date', ''))

        # Section 1 Values
        # (૧) Full Name
        draw_val(276, 187, 410, data.get('full_name', ''))

        # (૨) Correspondence Address (up to 2 lines)
        addr = str(data.get('address', '')).strip()
        if len(addr) > 45:
            split_idx = addr.rfind(',', 0, 50)
            if split_idx == -1:
                split_idx = addr.rfind(' ', 0, 50)
            if split_idx == -1 or split_idx < 20:
                split_idx = 45
            else:
                split_idx += 1
            part1 = addr[:split_idx].strip()
            part2 = addr[split_idx:].strip()
            draw_val(336, 211, 350, part1)
            draw_val(60, 233, 625, part2)
        else:
            draw_val(336, 211, 350, addr)

        # (૩) Village Address (ગામનું સરનામું - up to 2 lines)
        v_addr = str(data.get('village_address', '')).strip()
        if len(v_addr) > 50:
            split_idx = v_addr.rfind(',', 0, 55)
            if split_idx == -1:
                split_idx = v_addr.rfind(' ', 0, 55)
            if split_idx == -1 or split_idx < 20:
                split_idx = 50
            else:
                split_idx += 1
            v_part1 = v_addr[:split_idx].strip()
            v_part2 = v_addr[split_idx:].strip()
            draw_val(176, 258, 510, v_part1)
            draw_val(60, 280, 625, v_part2)
        else:
            draw_val(176, 258, 510, v_addr)

        # (૪) Email
        draw_val(152, 305, 535, data.get('email', ''))

        # (૫) Education / શિક્ષણ (Official Field ૫ in Section 1)
        draw_val(126, 328, 560, data.get('education', ''))

        # (૬) Mobile & Landline
        draw_val(158, 352, 260, data.get('mobile', ''))
        draw_val(508, 352, 178, data.get('phone_landline', ''))

        # Section 2 Values
        # (૭) Occupation
        draw_val(186, 419, 500, data.get('occupation', ''))

        # (૮) Business Address
        b_addr = str(data.get('business_address', '')).strip()
        if len(b_addr) > 45:
            split_idx = b_addr.rfind(',', 0, 50)
            if split_idx == -1:
                split_idx = b_addr.rfind(' ', 0, 50)
            if split_idx == -1 or split_idx < 20:
                split_idx = 45
            else:
                split_idx += 1
            b_part1 = b_addr[:split_idx].strip()
            b_part2 = b_addr[split_idx:].strip()
            draw_val(246, 445, 440, b_part1)
            draw_val(60, 468, 625, b_part2)
        else:
            draw_val(246, 445, 440, b_addr)

        # (૯) Blood Group
        draw_val(154, 501, 305, data.get('blood_group', ''))

        # Section 3 Values
        # (૧૦) Samaj
        draw_val(126, 565, 560, data.get('samaj', ''))

        # (૧૧) Membership Fee & Signature
        draw_val(126, 592, 125, data.get('membership_fee', ''))

        sig_img = data.get('signature_image', '')
        if sig_img and os.path.exists(sig_img):
            pix = QPixmap(sig_img)
            if not pix.isNull():
                scaled_pix = pix.scaled(145, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                offset_x = (145.0 - scaled_pix.width()) / 2.0
                offset_y = 24.0 - scaled_pix.height()
                p.drawPixmap(QPointF(530.0 + offset_x, 565.0 + offset_y), scaled_pix)
            else:
                sig_text = data.get('signature_text') or data.get('signature') or data.get('full_name', '')
                draw_val(532, 592, 150, sig_text)
        else:
            sig_text = data.get('signature_text') or data.get('signature') or data.get('full_name', '')
            draw_val(532, 592, 150, sig_text)

        # Section 4 Family Members Table Values (up to 10 rows)
        tbl_val_font = QFont(font_family)
        tbl_val_font.setPixelSize(10)
        p.setFont(tbl_val_font)
        family_rows = data.get('family_members', [])
        for r_idx in range(min(10, len(family_rows))):
            fm = family_rows[r_idx]
            ry = TABLE_HDR_BOT_Y + r_idx * TABLE_ROW_H
            rh = TABLE_ROW_H

            # Col 1: નામ
            rect1 = QRectF(COL_X[1] + 4, ry, COL_X[2] - COL_X[1] - 8, rh)
            p.drawText(rect1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(fm.get('name', '')))

            # Col 2: સંબંધ
            rel_raw = str(fm.get('relation', '')).strip()
            rel_text = rel_raw.split('(')[0].strip() if '(' in rel_raw else rel_raw
            rect2 = QRectF(COL_X[2] + 2, ry, COL_X[3] - COL_X[2] - 4, rh)
            p.drawText(rect2, Qt.AlignmentFlag.AlignCenter, rel_text)

            # Col 3: ઉંમર
            age_val = str(fm.get('age', ''))
            rect3 = QRectF(COL_X[3] + 2, ry, COL_X[4] - COL_X[3] - 4, rh)
            p.drawText(rect3, Qt.AlignmentFlag.AlignCenter, age_val)

            # Col 4: અભ્યાસ
            rect4 = QRectF(COL_X[4] + 2, ry, COL_X[5] - COL_X[4] - 4, rh)
            p.drawText(rect4, Qt.AlignmentFlag.AlignCenter, str(fm.get('education', '')))

            # Col 5: બ્લડ ગ્રુપ
            rect5 = QRectF(COL_X[5] + 2, ry, COL_X[6] - COL_X[5] - 4, rh)
            p.drawText(rect5, Qt.AlignmentFlag.AlignCenter, str(fm.get('blood_group', '')))

            # Col 6: વ્યવસાય
            rect6 = QRectF(COL_X[6] + 2, ry, COL_X[7] - COL_X[6] - 4, rh)
            p.drawText(rect6, Qt.AlignmentFlag.AlignCenter, str(fm.get('occupation', '')))

            # Col 7: સંપર્ક નંબર
            rect7 = QRectF(COL_X[7] + 2, ry, COL_X[8] - COL_X[7] - 4, rh)
            p.drawText(rect7, Qt.AlignmentFlag.AlignCenter, str(fm.get('contact_number', '')))
