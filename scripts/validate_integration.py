#!/usr/bin/env python3
"""
통합 검증 스크립트
- RULE.md와 실제 코드 간 일관성 검증
- 파일 간 참조 관계 검증
- 함수명, API 엔드포인트 일관성 검증
"""

import os
import re
from pathlib import Path

class IntegrationValidator:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.errors = []
        self.warnings = []
        
    def validate_file_references(self):
        """RULE.md에서 언급한 파일들이 실제로 존재하는지 확인"""
        rule_files = [
            '.cursor/rules/frontend-rule/RULE.md',
            '.cursor/rules/backend-rule/RULE.md',
            '.cursor/rules/uiux-rule/RULE.md',
            '.cursor/rules/Planner/RULE.md',
            '.cursor/rules/uiux-rule/CHART_STANDARD.md'
        ]
        
        for rule_file in rule_files:
            rule_path = self.base_dir / rule_file
            if not rule_path.exists():
                self.warnings.append(f"Rule file not found: {rule_file}")
                continue
                
            try:
                content = rule_path.read_text(encoding='utf-8')
                
                # @frontend, @server, @docs 참조 찾기
                refs = re.findall(r'@([\w/.-]+)', content)
                for ref in refs:
                    # 파일 경로로 변환
                    if ref.startswith('frontend/'):
                        file_path = self.base_dir / ref
                    elif ref.startswith('server/'):
                        file_path = self.base_dir / ref
                    elif ref.startswith('docs/'):
                        file_path = self.base_dir / ref
                    else:
                        # 상대 경로 처리
                        if '/' in ref:
                            file_path = self.base_dir / ref
                        else:
                            continue
                            
                    if not file_path.exists():
                        self.errors.append(f"{rule_file} references non-existent file: {ref}")
            except Exception as e:
                self.warnings.append(f"Error reading {rule_file}: {str(e)}")
    
    def validate_function_names(self):
        """RULE.md에서 언급한 함수들이 실제 코드에 존재하는지 확인"""
        # Frontend 함수 검증
        frontend_file = self.base_dir / 'frontend/ai_studio_code_F2.html'
        if frontend_file.exists():
            try:
                frontend_content = frontend_file.read_text(encoding='utf-8')
                
                # RULE.md에서 언급한 주요 함수들
                mentioned_functions = [
                    'updateChart', 'showTooltip', 'processExchangeRateData',
                    'initInflation', 'fetchInflationData', 'updateInflationChart',
                    'initGDP', 'fetchGDPData', 'updateGDPChart',
                    'initInterestRates', 'fetchInterestRateData', 'updateInterestChart',
                    'switchProduct', 'formatDateForAPI', 'validateDateRange'
                ]
                
                for func in mentioned_functions:
                    pattern = rf'function\s+{func}\s*\('
                    if not re.search(pattern, frontend_content):
                        self.warnings.append(f"Function mentioned in RULE.md but not found: {func}")
            except Exception as e:
                self.warnings.append(f"Error reading frontend file: {str(e)}")
        
        # Backend 함수 검증
        backend_file = self.base_dir / 'server/bok_backend.py'
        if backend_file.exists():
            try:
                backend_content = backend_file.read_text(encoding='utf-8')
                
                mentioned_functions = [
                    'get_bok_statistics', 'get_market_index', 'validate_date_format',
                    'format_date_for_cycle', 'calculate_statistics', 'get_category_info'
                ]
                
                for func in mentioned_functions:
                    pattern = rf'def\s+{func}\s*\('
                    if not re.search(pattern, backend_content):
                        self.warnings.append(f"Function mentioned in RULE.md but not found: {func}")
            except Exception as e:
                self.warnings.append(f"Error reading backend file: {str(e)}")
    
    def validate_api_endpoints(self):
        """RULE.md와 실제 코드의 API 엔드포인트 일관성 확인"""
        main_file = self.base_dir / 'server/main.py'
        if not main_file.exists():
            self.warnings.append("server/main.py not found")
            return
            
        try:
            main_content = main_file.read_text(encoding='utf-8')
            
            # 실제 정의된 엔드포인트 찾기
            endpoints = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', main_content)
            
            # RULE.md에서 언급된 엔드포인트와 비교
            expected_endpoints = [
                '/api/market/indices',
                '/api/market/indices/stats',
                '/api/market/indices/multi',
                '/api/market/categories',
                '/api/bok/stats'
            ]
            
            for endpoint in expected_endpoints:
                if endpoint not in endpoints:
                    self.warnings.append(f"Expected endpoint not found: {endpoint}")
        except Exception as e:
            self.warnings.append(f"Error reading main.py: {str(e)}")
    
    def validate_css_variables(self):
        """RULE.md에서 언급한 CSS 변수가 실제 코드에 정의되어 있는지 확인"""
        frontend_file = self.base_dir / 'frontend/ai_studio_code_F2.html'
        if not frontend_file.exists():
            return
            
        try:
            frontend_content = frontend_file.read_text(encoding='utf-8')
            
            # RULE.md에서 언급한 CSS 변수들
            css_vars = [
                '--bg-color', '--text-main', '--text-sub', '--accent-color',
                '--c-usd', '--c-eur', '--c-jpy', '--c-cpi-total', '--c-gdp-total'
            ]
            
            for var in css_vars:
                pattern = rf'{re.escape(var)}\s*:'
                if not re.search(pattern, frontend_content):
                    self.warnings.append(f"CSS variable mentioned in RULE.md but not found: {var}")
        except Exception as e:
            self.warnings.append(f"Error reading frontend file for CSS validation: {str(e)}")
    
    def validate_bok_mapping(self):
        """BOK_MAPPING에 정의된 카테고리가 실제로 사용되는지 확인"""
        backend_file = self.base_dir / 'server/bok_backend.py'
        if not backend_file.exists():
            return
            
        try:
            backend_content = backend_file.read_text(encoding='utf-8')
            
            # BOK_MAPPING에서 카테고리 추출
            categories = re.findall(r'"(exchange|inflation|gdp|money|sentiment|balance|interest)":', backend_content)
            
            # main.py에서 실제 사용되는지 확인
            # main.py는 type 파라미터를 받아서 get_market_index()를 호출하므로
            # 모든 카테고리가 사용 가능함 (동적 처리)
            # 대신 get_market_index 함수가 모든 카테고리를 지원하는지 확인
            main_file = self.base_dir / 'server/main.py'
            if main_file.exists():
                main_content = main_file.read_text(encoding='utf-8')
                if 'get_market_index' not in main_content:
                    self.warnings.append("get_market_index function not found in main.py")
                elif 'category' not in main_content.lower():
                    self.warnings.append("Category parameter handling not found in main.py")
        except Exception as e:
            self.warnings.append(f"Error validating BOK_MAPPING: {str(e)}")
    
    def validate_frontend_html_structure(self):
        """프론트엔드 HTML 구조 검증"""
        frontend_file = self.base_dir / 'frontend/ai_studio_code_F2.html'
        if not frontend_file.exists():
            self.errors.append("Frontend file not found: frontend/ai_studio_code_F2.html")
            return
            
        try:
            content = frontend_file.read_text(encoding='utf-8')
            
            # 필수 패널 ID 확인
            required_panels = [
                'economy-panel',
                'interest-rates-panel',
                'inflation-panel',
                'gdp-panel'
            ]
            
            for panel_id in required_panels:
                if f'id="{panel_id}"' not in content and f"id='{panel_id}'" not in content:
                    self.warnings.append(f"Required panel not found: {panel_id}")
        except Exception as e:
            self.warnings.append(f"Error validating frontend HTML structure: {str(e)}")
    
    def validate_inflation_gdp_functions(self):
        """Inflation과 GDP 관련 함수 검증"""
        frontend_file = self.base_dir / 'frontend/ai_studio_code_F2.html'
        if not frontend_file.exists():
            return
            
        try:
            content = frontend_file.read_text(encoding='utf-8')
            
            # Inflation 관련 필수 함수
            inflation_functions = [
                'initInflation',
                'fetchInflationData',
                'updateInflationChart',
                'renderInflationYAxisLabels',
                'renderInflationXAxisLabels',
                'updateInflationChartHeader',
                'toggleInflationItem',
                # 'setInflationPeriod' - 제거됨 (주기 버튼으로 대체)
            ]
            
            for func in inflation_functions:
                pattern = rf'function\s+{func}\s*\('
                if not re.search(pattern, content):
                    self.errors.append(f"Inflation function not found: {func}")
            
            # GDP 관련 필수 함수
            gdp_functions = [
                'initGDP',
                'fetchGDPData',
                'updateGDPChart',
                'renderGDPYAxisLabels',
                'renderGDPXAxisLabels',
                'updateGDPChartHeader',
                'toggleGDPItem',
                'setGDPPeriod'
            ]
            
            for func in gdp_functions:
                pattern = rf'function\s+{func}\s*\('
                if not re.search(pattern, content):
                    self.errors.append(f"GDP function not found: {func}")
            
            # Inflation 패널 HTML 요소 확인
            inflation_elements = [
                'inflation-panel',
                'inflation-start-date',
                'inflation-end-date',
                'inflation-chart-container',
                'inflation-chart-svg',
                'inflation-chart-header'
            ]
            
            for elem_id in inflation_elements:
                if f'id="{elem_id}"' not in content and f"id='{elem_id}'" not in content:
                    self.errors.append(f"Inflation HTML element not found: {elem_id}")
            
            # GDP 패널 HTML 요소 확인
            gdp_elements = [
                'gdp-panel',
                'gdp-start-date',
                'gdp-end-date',
                'gdp-chart-container',
                'gdp-chart-svg',
                'gdp-chart-header'
            ]
            
            for elem_id in gdp_elements:
                if f'id="{elem_id}"' not in content and f"id='{elem_id}'" not in content:
                    self.errors.append(f"GDP HTML element not found: {elem_id}")
            
            # CSS 변수 확인
            css_vars = [
                '--c-cpi-total',
                '--c-cpi-fresh',
                '--c-cpi-industrial',
                '--c-gdp-total',
                '--c-gdp-consumption',
                '--c-gdp-investment'
            ]
            
            for var in css_vars:
                pattern = rf'{re.escape(var)}\s*:'
                if not re.search(pattern, content):
                    self.errors.append(f"CSS variable not found: {var}")
                    
        except Exception as e:
            self.warnings.append(f"Error validating Inflation/GDP functions: {str(e)}")
    
    def validate_inflation_gdp_backend(self):
        """Inflation과 GDP 백엔드 검증"""
        backend_file = self.base_dir / 'server/bok_backend.py'
        if not backend_file.exists():
            return
            
        try:
            content = backend_file.read_text(encoding='utf-8')
            
            # BOK_MAPPING에 inflation과 gdp가 정의되어 있는지 확인
            if '"inflation":' not in content:
                self.errors.append("Inflation category not found in BOK_MAPPING")
            else:
                # Inflation 항목 확인
                if 'CPI_TOTAL' not in content or 'CPI_FRESH' not in content or 'CPI_INDUSTRIAL' not in content:
                    self.warnings.append("Some Inflation items (CPI_TOTAL, CPI_FRESH, CPI_INDUSTRIAL) not found in BOK_MAPPING")
            
            if '"gdp":' not in content:
                self.errors.append("GDP category not found in BOK_MAPPING")
            else:
                # GDP 항목 확인
                if 'GDP_TOTAL' not in content or 'GDP_CONSUMPTION' not in content or 'GDP_INVESTMENT' not in content:
                    self.warnings.append("Some GDP items (GDP_TOTAL, GDP_CONSUMPTION, GDP_INVESTMENT) not found in BOK_MAPPING")
                    
        except Exception as e:
            self.warnings.append(f"Error validating Inflation/GDP backend: {str(e)}")
    
    def validate_chart_standards(self):
        """차트 표준 준수 검증"""
        frontend_file = self.base_dir / 'frontend/ai_studio_code_F2.html'
        if not frontend_file.exists():
            self.warnings.append("Frontend file not found for chart validation")
            return
        
        try:
            content = frontend_file.read_text(encoding='utf-8')
            
            # viewBox 표준 검증 (1200 400)
            viewbox_pattern = r'viewBox="0 0 (\d+) (\d+)"'
            viewboxes = re.findall(viewbox_pattern, content)
            for width, height in viewboxes:
                if width != '1200' or height != '400':
                    self.warnings.append(f"Non-standard viewBox found: 0 0 {width} {height} (should be 0 0 1200 400)")
            
            # padding 표준 검증
            padding_pattern = r'padding\s*=\s*\{\s*top:\s*(\d+),\s*bottom:\s*(\d+),\s*left:\s*(\d+),\s*right:\s*(\d+)\s*\}'
            paddings = re.findall(padding_pattern, content)
            for top, bottom, left, right in paddings:
                if top != '20' or bottom != '30' or left != '40' or right != '20':
                    self.warnings.append(f"Non-standard padding found: top={top}, bottom={bottom}, left={left}, right={right} (should be top=20, bottom=30, left=40, right=20)")
            
        except Exception as e:
            self.errors.append(f"Error validating chart standards: {e}")
    
    def validate_agent_rules(self):
        """AGENT_RULE.md 파일들이 존재하는지 확인"""
        agent_rule_files = [
            '.cursor/rules/frontend-rule/AGENT_RULE.md',
            '.cursor/rules/backend-rule/AGENT_RULE.md',
            '.cursor/rules/uiux-rule/AGENT_RULE.md',
            '.cursor/rules/Planner/AGENTRULE.md'
        ]
        
        for rule_file in agent_rule_files:
            rule_path = self.base_dir / rule_file
            if not rule_path.exists():
                self.warnings.append(f"AGENT_RULE file not found: {rule_file}")
    
    def run_all_checks(self):
        """모든 검증 실행"""
        print("=" * 60)
        print("Integration Validation")
        print("=" * 60)
        print()
        
        print("1. Validating file references...")
        self.validate_file_references()
        
        print("2. Validating function names...")
        self.validate_function_names()
        
        print("3. Validating API endpoints...")
        self.validate_api_endpoints()
        
        print("4. Validating CSS variables...")
        self.validate_css_variables()
        
        print("5. Validating BOK_MAPPING...")
        self.validate_bok_mapping()
        
        print("6. Validating frontend HTML structure...")
        self.validate_frontend_html_structure()
        
        print("7. Validating AGENT_RULE files...")
        self.validate_agent_rules()
        
        print("8. Validating Inflation/GDP functions...")
        self.validate_inflation_gdp_functions()
        
        print("9. Validating Inflation/GDP backend...")
        self.validate_inflation_gdp_backend()
        
        print("10. Validating chart standards...")
        self.validate_chart_standards()
        
        print()
        print("=" * 60)
        print("Validation Results")
        print("=" * 60)
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print()
        
        if self.errors:
            print("[ERROR] Must be fixed:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            print()
        
        if self.warnings:
            print("[WARNING] Should be reviewed:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("[SUCCESS] All checks passed!")
            print()
        
        return len(self.errors) == 0

if __name__ == '__main__':
    import sys
    
    # 현재 스크립트의 부모 디렉토리를 base_dir로 사용
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    validator = IntegrationValidator(base_dir)
    success = validator.run_all_checks()
    
    sys.exit(0 if success else 1)

