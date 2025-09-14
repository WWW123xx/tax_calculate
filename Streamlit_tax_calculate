import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# 设置页面配置
st.set_page_config(
    page_title="公积金优化计算器",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置中文字体支持
def set_chinese_font():
    try:
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        st.warning("中文字体设置可能不成功，图表可能显示乱码")

# 在程序开始时调用
set_chinese_font()

class TaxCalculator:
    """个人所得税计算器（支持年终奖两种计税方式）"""

    # 个税税率表（综合所得）
    TAX_BRACKETS = [
        (0, 36000, 0.03, 0),
        (36000, 144000, 0.10, 2520),
        (144000, 300000, 0.20, 16920),
        (300000, 420000, 0.25, 31920),
        (420000, 660000, 0.30, 52920),
        (660000, 960000, 0.35, 85920),
        (960000, float('inf'), 0.45, 181920)
    ]

    # 年终奖单独计税税率表
    BONUS_TAX_BRACKETS = [
        (0, 3000, 0.03, 0),
        (3000, 12000, 0.10, 210),
        (12000, 25000, 0.20, 1410),
        (25000, 35000, 0.25, 2660),
        (35000, 55000, 0.30, 4410),
        (55000, 80000, 0.35, 7160),
        (80000, float('inf'), 0.45, 15160)
    ]

    def __init__(self, monthly_salary, annual_bonus, social_insurance,
                 special_deduction=0, other_deductions=0, 公积金比例=0.12,
                 company_base=7000):
        self.monthly_salary = monthly_salary
        self.annual_bonus = annual_bonus
        self.social_insurance = social_insurance
        self.special_deduction = special_deduction
        self.other_deductions = other_deductions
        self.公积金比例 = 公积金比例
        self.company_base = company_base

    def calculate_tax(self, annual_taxable_income):
        """计算年度综合所得税"""
        for lower, upper, rate, deduction in self.TAX_BRACKETS:
            if lower <= annual_taxable_income < upper:
                return annual_taxable_income * rate - deduction
        return annual_taxable_income * 0.45 - 181920

    def calculate_bonus_tax_separate(self, bonus):
        """计算年终奖单独计税"""
        monthly_bonus = bonus / 12

        for lower, upper, rate, deduction in self.BONUS_TAX_BRACKETS:
            if lower <= monthly_bonus < upper:
                return bonus * rate - deduction

        return bonus * 0.45 - 15160

    def calculate_scenario(self, target_base, bonus_tax_method="combined"):
        """计算指定基数下的情况

        Args:
            target_base: 目标公积金基数
            bonus_tax_method: 年终奖计税方式，"combined"为并入综合所得，"separate"为单独计税
        """
        # 1. 计算公积金部分
        # 个人应缴公积金
        personal_pf = target_base * self.公积金比例

        # 公司应缴公积金（按目标基数计算）
        company_pf = target_base * self.公积金比例

        # 如果目标基数高于公司基数，个人需要额外支付公司多付的部分
        if target_base > self.company_base:
            # 公司原本应缴的部分
            company_original_pf = self.company_base * self.公积金比例
            # 公司多付的部分（由个人承担）
            company_extra_pf = company_pf - company_original_pf
            # 个人需要额外支付的金额
            extra_payment = company_extra_pf
        else:
            extra_payment = 0
            company_extra_pf = 0

        # 2. 计算应纳税所得额（税前扣除个人公积金部分）
        monthly_taxable = (self.monthly_salary - self.social_insurance - personal_pf -
                           5000 - self.special_deduction - self.other_deductions)
        monthly_taxable = max(0, monthly_taxable)

        # 年度应纳税所得额（不含年终奖）
        annual_taxable = monthly_taxable * 12

        # 3. 计算年度个税（根据不同的年终奖计税方式）
        if bonus_tax_method == "combined":  # 年终奖并入综合所得
            # 年度应纳税所得额（含年终奖）
            annual_taxable_with_bonus = annual_taxable + self.annual_bonus
            annual_tax = self.calculate_tax(annual_taxable_with_bonus)
            bonus_tax = 0  # 年终奖已并入，不单独计算
        else:  # 年终奖单独计税
            # 综合所得部分个税
            annual_income_tax = self.calculate_tax(annual_taxable)
            # 年终奖部分个税
            bonus_tax = self.calculate_bonus_tax_separate(self.annual_bonus)
            annual_tax = annual_income_tax + bonus_tax
            annual_taxable_with_bonus = annual_taxable  # 不包含年终奖

        # 4. 计算月度现金收入
        monthly_cash = (self.monthly_salary - self.social_insurance - personal_pf -
                        extra_payment - annual_tax / 12)

        # 5. 计算公积金账户总收入（个人+公司部分）
        total_pf_income = (personal_pf + company_pf) * 12

        # 6. 计算年度总收入
        total_income = monthly_cash * 12 + total_pf_income + self.annual_bonus

        return {
            '公积金基数': target_base,
            '个人公积金': personal_pf,
            '公司公积金': company_pf,
            '公司额外部分': company_extra_pf,
            '个人额外支付': extra_payment,
            '年度个税': annual_tax,
            '年终奖个税': bonus_tax if bonus_tax_method == "separate" else 0,
            '计税方式': "并入综合所得" if bonus_tax_method == "combined" else "单独计税",
            '月度现金收入': monthly_cash,
            '年度公积金收入': total_pf_income,
            '年度总收入': total_income,
            '年度应纳税所得额': annual_taxable_with_bonus
        }

def main():
    st.title("💰 公积金优化计算器（支持年终奖两种计税方式）")
    
    # 添加说明
    with st.expander("💡 使用说明和核心逻辑", expanded=True):
        st.markdown("""
        ### 核心逻辑：
        - 提高基数 → 公司和个人都多缴公积金 → 个人承担公司多缴部分
        - 但所有多缴部分都进入公积金账户 → 税前扣除增加 → 个税减少
        
        ### 使用方法：
        1. 在左侧输入您的工资和社保信息
        2. 选择年终奖计税方式
        3. 查看右侧的计算结果和分析
        4. 下载详细计算结果表格
        """)
    
    # 创建侧边栏用于输入
    with st.sidebar:
        st.header("参数设置")
        
        # 使用列布局使输入更紧凑
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_salary = st.number_input("月薪", min_value=0, value=22000, step=1000)
            annual_bonus = st.number_input("年终奖", min_value=0, value=60000, step=5000)
            social_base = st.number_input("社保基数", min_value=0, value=4812, step=100)
        
        with col2:
            special_deduction = st.number_input("专项附加扣除", min_value=0, value=1500, step=500)
            company_base = st.number_input("公司公积金基数", min_value=0, value=7000, step=1000)
            pf_ratio = st.slider("公积金比例", min_value=0.05, max_value=0.12, value=0.12, step=0.01)
        
        # 计算社保费用
        social_insurance = social_base * 0.08
        
        # 选择年终奖计税方式
        bonus_tax_method = st.radio(
            "年终奖计税方式",
            ["并入综合所得", "单独计税"],
            index=0,
            help="并入综合所得：年终奖与工资合并计算个税；单独计税：年终奖单独计算个税"
        )
        
        bonus_tax_method = "combined" if bonus_tax_method == "并入综合所得" else "separate"
        
        # 计算按钮
        calculate_clicked = st.button("开始计算", type="primary", use_container_width=True)
    
    # 主内容区域
    if calculate_clicked:
        # 显示计算进度
        with st.spinner("正在计算，请稍候..."):
            calculator = TaxCalculator(
                monthly_salary, annual_bonus, social_insurance,
                special_deduction, 0, pf_ratio, company_base
            )

            # 计算不同基数
            bases = list(range(int(company_base), min(40694, int(company_base*3)), 500))
            results = []

            for base in bases:
                result = calculator.calculate_scenario(base, bonus_tax_method)
                results.append(result)

            df = pd.DataFrame(results)
            
            # 格式化显示
            display_df = df[['公积金基数', '个人公积金', '公司公积金', '公司额外部分', 
                            '个人额外支付', '年度个税', '月度现金收入', 
                            '年度公积金收入', '年度总收入']].copy()
            
            for col in display_df.columns:
                if col != '公积金基数':
                    display_df[col] = display_df[col].round(0).astype(int)
            
            # 分析结果
            best_idx = df['年度总收入'].idxmax()
            best = df.iloc[best_idx]
            base_case = df.iloc[0]  # 公司基数的情况
            
            # 显示结果表格
            st.header("📊 计算结果")
            st.dataframe(display_df.style.format("{:,.0f}"), use_container_width=True)
            
            # 显示分析结果
            st.header("🎯 结果分析")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="公司基数下年度总收入", 
                    value=f"{base_case['年度总收入']:,.0f}元"
                )
            
            with col2:
                st.metric(
                    label="最优基数下年度总收入", 
                    value=f"{best['年度总收入']:,.0f}元"
                )
            
            with col3:
                increase = best['年度总收入'] - base_case['年度总收入']
                st.metric(
                    label="收入增加", 
                    value=f"{increase:,.0f}元",
                    delta=f"{increase / base_case['年度总收入'] * 100:.2f}%" if increase > 0 else None
                )
            
            if best['年度总收入'] > base_case['年度总收入']:
                # 详细分析
                tax_saving = base_case['年度个税'] - best['年度个税']
                pf_increase = best['年度公积金收入'] - base_case['年度公积金收入']
                extra_cost = best['个人额外支付'] * 12
                
                st.success(f"✅ 提高基数可增加年收入: {increase:,.0f} 元 (+{increase / base_case['年度总收入'] * 100:.2f}%)")
                
                st.subheader("📈 详细分析")
                analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
                
                with analysis_col1:
                    st.info(f"个税减少: {tax_saving:,.0f} 元")
                
                with analysis_col2:
                    st.info(f"公积金增加: {pf_increase:,.0f} 元")
                
                with analysis_col3:
                    st.info(f"额外支付: {extra_cost:,.0f} 元")
                
                st.info(f"净收益: {tax_saving + pf_increase - extra_cost:,.0f} 元")
            else:
                st.error("❌ 提高基数反而减少收入")
            
            # 特别分析从公司基数到最优基数的情况
            st.subheader("🔍 基数调整分析")
            base_company = df[df['公积金基数'] == company_base].iloc[0]
            base_best = df[df['公积金基数'] == best['公积金基数']].iloc[0]
            
            st.write(f"从 **{company_base}元** 提高到 **{best['公积金基数']}元**:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"个人公积金: {base_company['个人公积金']:.0f} → {base_best['个人公积金']:.0f}")
                st.write(f"(+{base_best['个人公积金'] - base_company['个人公积金']:.0f})")
            
            with col2:
                st.write(f"公司公积金: {base_company['公司公积金']:.0f} → {base_best['公司公积金']:.0f}")
                st.write(f"(+{base_best['公司公积金'] - base_company['公司公积金']:.0f})")
            
            with col3:
                st.write(f"个人额外支付: {base_best['个人额外支付']:.0f}")
                st.write(f"(公司多付部分)")
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.write(f"个税减少: {base_company['年度个税'] - base_best['年度个税']:,.0f} 元")
            
            with col5:
                st.write(f"公积金增加: {base_best['年度公积金收入'] - base_company['年度公积金收入']:,.0f} 元")
            
            with col6:
                st.write(f"总收入增加: {base_best['年度总收入'] - base_company['年度总收入']:,.0f} 元")
            
            # 绘制图表
            st.header("📈 可视化分析")
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 年度总收入图表
            axes[0, 0].plot(df['公积金基数'], df['年度总收入'], 'g-', linewidth=2, marker='o', markersize=4)
            axes[0, 0].axvline(x=company_base, color='r', linestyle='--', alpha=0.7, label=f'公司基数 ({company_base})')
            if best['公积金基数'] != company_base:
                axes[0, 0].axvline(x=best['公积金基数'], color='orange', linestyle='--', alpha=0.7, label=f'最优 ({best["公积金基数"]})')
            axes[0, 0].set_xlabel('公积金基数 (元)')
            axes[0, 0].set_ylabel('年度总收入 (元)')
            axes[0, 0].set_title(f'年度总收入 vs 公积金基数\n(年终奖计税方式: {results[0]["计税方式"]})')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # 年度个税图表
            axes[0, 1].plot(df['公积金基数'], df['年度个税'], 'r-', linewidth=2, marker='o', markersize=4)
            axes[0, 1].set_xlabel('公积金基数 (元)')
            axes[0, 1].set_ylabel('年度个税 (元)')
            axes[0, 1].set_title('年度个税 vs 公积金基数')
            axes[0, 1].grid(True, alpha=0.3)
            
            # 月度收入图表
            axes[1, 0].plot(df['公积金基数'], df['月度现金收入'], 'b-', linewidth=2, marker='o', markersize=4, label='月度现金收入')
            axes[1, 0].plot(df['公积金基数'], (df['个人公积金'] + df['公司公积金']), color='orange', linewidth=2, marker='o', markersize=4,
                         label='月度公积金')
            axes[1, 0].set_xlabel('公积金基数 (元)')
            axes[1, 0].set_ylabel('月度金额 (元)')
            axes[1, 0].set_title('现金收入 vs 公积金收入')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            
            # 收入增加图表
            income_increase = df['年度总收入'] - base_case['年度总收入']
            axes[1, 1].bar(df['公积金基数'], income_increase, alpha=0.6, color='green')
            axes[1, 1].set_xlabel('公积金基数 (元)')
            axes[1, 1].set_ylabel('收入增加金额 (元)')
            axes[1, 1].set_title('相比公司基数的收入增加金额')
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 提供决策建议
            st.header("💡 决策建议")
            
            if best['公积金基数'] > company_base:
                st.success(f"""
                建议将公积金基数提高到 **{best['公积金基数']:,.0f} 元**
                
                - 每年可增加收入 **{best['年度总收入'] - base_case['年度总收入']:,.0f} 元**
                - 虽然每月现金收入减少 **{base_case['月度现金收入'] - best['月度现金收入']:,.0f} 元**
                - 但公积金账户增加 **{best['年度公积金收入'] - base_case['年度公积金收入']:,.0f} 元/年**
                - 且个税减少 **{base_case['年度个税'] - best['年度个税']:,.0f} 元/年**
                """)
            else:
                st.info(f"保持公司基数 **{company_base} 元**是最优选择")
            
            # 比较两种年终奖计税方式
            st.header("📋 年终奖计税方式比较")
            
            # 计算公司基数下两种方式的差异
            base_result_combined = calculator.calculate_scenario(company_base, "combined")
            base_result_separate = calculator.calculate_scenario(company_base, "separate")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("并入综合所得")
                st.metric("年度个税", f"{base_result_combined['年度个税']:,.0f}元")
                st.metric("年度总收入", f"{base_result_combined['年度总收入']:,.0f}元")
            
            with col2:
                st.subheader("单独计税")
                st.metric("年度个税", f"{base_result_separate['年度个税']:,.0f}元")
                st.metric("年度总收入", f"{base_result_separate['年度总收入']:,.0f}元")
            
            if base_result_combined['年度个税'] < base_result_separate['年度个税']:
                tax_saving = base_result_separate['年度个税'] - base_result_combined['年度个税']
                st.success(f"💡 建议: 并入综合所得方式更优，可节省个税 {tax_saving:,.0f} 元")
            else:
                tax_saving = base_result_combined['年度个税'] - base_result_separate['年度个税']
                st.success(f"💡 建议: 单独计税方式更优，可节省个税 {tax_saving:,.0f} 元")
            
            # 添加下载功能
            st.header("📥 下载计算结果")
            
            # 将DataFrame转换为CSV
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="下载完整数据 (CSV)",
                data=csv,
                file_name="公积金优化计算结果.csv",
                mime="text/csv",
            )
    
    else:
        # 显示初始提示
        st.info("请在左侧输入参数后点击「开始计算」按钮")

if __name__ == "__main__":
    main()
