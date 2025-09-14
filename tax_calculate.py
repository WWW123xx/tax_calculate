import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
import numpy as np


# 设置中文字体支持
def set_chinese_font():
    try:
        # 尝试使用系统自带的中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        print("已设置中文字体支持")
    except:
        print("警告: 中文字体设置可能不成功，图表可能显示乱码")


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


def get_user_input():
    """获取用户输入的所有参数"""
    print("=" * 60)
    print("公积金优化计算器参数输入")
    print("=" * 60)

    # 提供默认值并让用户输入
    default_values = {
        "月薪": 22000,
        "年终奖": 60000,
        "社保基数": 4812,
        "专项附加扣除": 1500,
        "公司公积金基数": 7000,
        "公积金比例": 0.12
    }

    inputs = {}

    for param, default in default_values.items():
        prompt = f"请输入{param} (默认: {default}): "
        value = input(prompt).strip()

        if value == "":
            inputs[param] = default
        else:
            try:
                inputs[param] = float(value) if "." in value else int(value)
            except ValueError:
                print(f"输入无效，使用默认值 {default}")
                inputs[param] = default

    # 选择年终奖计税方式
    print("\n请选择年终奖计税方式:")
    print("1. 并入综合所得")
    print("2. 单独计税")
    choice = input("请输入选择 (1 或 2, 默认为1): ").strip()

    if choice == "2":
        bonus_tax_method = "separate"
        print("已选择: 年终奖单独计税")
    else:
        bonus_tax_method = "combined"
        print("已选择: 年终奖并入综合所得")
    inputs["社保费用"] = inputs["社保基数"] * 0.08
    return inputs, bonus_tax_method


def main():
    print("公积金优化计算器（支持年终奖两种计税方式）")
    print("=" * 70)
    print("💡 核心逻辑：")
    print("   提高基数 → 公司和个人都多缴公积金 → 个人承担公司多缴部分")
    print("   但所有多缴部分都进入公积金账户 → 税前扣除增加 → 个税减少")
    print("=" * 70)

    # 获取用户输入
    inputs, bonus_tax_method = get_user_input()

    # 使用用户输入的参数
    monthly_salary = inputs["月薪"]
    annual_bonus = inputs["年终奖"]
    social_insurance = inputs["社保费用"]
    special_deduction = inputs["专项附加扣除"]
    company_base = inputs["公司公积金基数"]

    calculator = TaxCalculator(
        monthly_salary, annual_bonus, social_insurance,
        special_deduction, 0, inputs["公积金比例"], company_base
    )

    # 计算不同基数
    bases = list(range(int(company_base), int(company_base * 2.5) + 1, 500))  # 从公司基数到2.5倍公司基数
    results = []

    for base in bases:
        result = calculator.calculate_scenario(base, bonus_tax_method)
        results.append(result)

    df = pd.DataFrame(results)

    # 显示结果
    print(f"\n📊 计算结果 (年终奖计税方式: {results[0]['计税方式']}):")
    print("=" * 130)

    display_df = df[['公积金基数', '个人公积金', '公司公积金', '公司额外部分', '个人额外支付', '年度个税', '月度现金收入', '年度公积金收入', '年度总收入']].copy()
    for col in display_df.columns:
        if col != '公积金基数':
            display_df[col] = display_df[col].round(0).astype(int)

    print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))

    # 分析结果
    best_idx = df['年度总收入'].idxmax()
    best = df.iloc[best_idx]
    base_case = df.iloc[0]  # 公司基数7000的情况

    print(f"\n🎯 结果分析:")
    print(f"   公司基数 {company_base} 元 → 年度总收入: {base_case['年度总收入']:,.0f} 元")
    print(f"   最优基数 {best['公积金基数']:,.0f} 元 → 年度总收入: {best['年度总收入']:,.0f} 元")

    if best['年度总收入'] > base_case['年度总收入']:
        increase = best['年度总收入'] - base_case['年度总收入']
        print(f"   ✅ 提高基数可增加年收入: {increase:,.0f} 元 (+{increase / base_case['年度总收入'] * 100:.2f}%)")

        # 详细分析
        tax_saving = base_case['年度个税'] - best['年度个税']
        pf_increase = best['年度公积金收入'] - base_case['年度公积金收入']
        extra_cost = best['个人额外支付'] * 12

        print(f"\n📈 详细分析:")
        print(f"   个税减少: {tax_saving:,.0f} 元")
        print(f"   公积金增加: {pf_increase:,.0f} 元")
        print(f"   额外支付: {extra_cost:,.0f} 元")
        print(f"   净收益: {tax_saving + pf_increase - extra_cost:,.0f} 元")
    else:
        print(f"   ❌ 提高基数反而减少收入")

    # 特别分析从公司基数到最优基数的情况
    base_company = df[df['公积金基数'] == company_base].iloc[0]
    base_best = df[df['公积金基数'] == best['公积金基数']].iloc[0]

    print(f"\n🔍 特别分析: 从{company_base}元提高到{best['公积金基数']}元")
    print(f"   个人公积金: {base_company['个人公积金']} → {base_best['个人公积金']} (+{base_best['个人公积金'] - base_company['个人公积金']})")
    print(f"   公司公积金: {base_company['公司公积金']} → {base_best['公司公积金']} (+{base_best['公司公积金'] - base_company['公司公积金']})")
    print(f"   个人额外支付: {base_best['个人额外支付']} (公司多付部分)")
    print(f"   个税减少: {base_company['年度个税'] - base_best['年度个税']:,.0f} 元")
    print(f"   公积金增加: {base_best['年度公积金收入'] - base_company['年度公积金收入']:,.0f} 元")
    print(f"   总收入增加: {base_best['年度总收入'] - base_company['年度总收入']:,.0f} 元")

    # 绘制图表
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    plt.plot(df['公积金基数'], df['年度总收入'], 'g-', linewidth=2, marker='o', markersize=4)
    plt.axvline(x=company_base, color='r', linestyle='--', alpha=0.7, label=f'公司基数 ({company_base})')
    if best['公积金基数'] != company_base:
        plt.axvline(x=best['公积金基数'], color='orange', linestyle='--', alpha=0.7, label=f'最优 ({best["公积金基数"]})')
    plt.xlabel('公积金基数 (元)')
    plt.ylabel('年度总收入 (元)')
    plt.title(f'年度总收入 vs 公积金基数\n(年终奖计税方式: {results[0]["计税方式"]})')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 2)
    plt.plot(df['公积金基数'], df['年度个税'], 'r-', linewidth=2, marker='o', markersize=4)
    plt.xlabel('公积金基数 (元)')
    plt.ylabel('年度个税 (元)')
    plt.title('年度个税 vs 公积金基数')
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 3)
    plt.plot(df['公积金基数'], df['月度现金收入'], 'b-', linewidth=2, marker='o', markersize=4, label='月度现金收入')
    plt.plot(df['公积金基数'], (df['个人公积金'] + df['公司公积金']), color='orange', linewidth=2, marker='o', markersize=4,
             label='月度公积金')
    plt.xlabel('公积金基数 (元)')
    plt.ylabel('月度金额 (元)')
    plt.title('现金收入 vs 公积金收入')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 4)
    # 计算收入增加金额
    income_increase = df['年度总收入'] - base_case['年度总收入']
    plt.bar(df['公积金基数'], income_increase, alpha=0.6, color='green')
    plt.xlabel('公积金基数 (元)')
    plt.ylabel('收入增加金额 (元)')
    plt.title('相比公司基数的收入增加金额')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # 提供决策建议
    print(f"\n💡 决策建议:")
    if best['公积金基数'] > company_base:
        print(f"   建议将公积金基数提高到 {best['公积金基数']:,.0f} 元")
        print(f"   每年可增加收入 {best['年度总收入'] - base_case['年度总收入']:,.0f} 元")
        print(f"   虽然每月现金收入减少 {base_case['月度现金收入'] - best['月度现金收入']:,.0f} 元")
        print(f"   但公积金账户增加 {best['年度公积金收入'] - base_case['年度公积金收入']:,.0f} 元/年")
        print(f"   且个税减少 {base_case['年度个税'] - best['年度个税']:,.0f} 元/年")
    else:
        print(f"   保持公司基数 {company_base} 元是最优选择")

    # 比较两种年终奖计税方式
    print(f"\n📋 年终奖计税方式比较:")

    # 计算公司基数下两种方式的差异
    base_result_combined = calculator.calculate_scenario(company_base, "combined")
    base_result_separate = calculator.calculate_scenario(company_base, "separate")

    print(f"   公司基数 {company_base} 元下:")
    print(f"     并入综合所得: 年度个税 {base_result_combined['年度个税']:,.0f} 元, 年度总收入 {base_result_combined['年度总收入']:,.0f} 元")
    print(f"     单独计税: 年度个税 {base_result_separate['年度个税']:,.0f} 元, 年度总收入 {base_result_separate['年度总收入']:,.0f} 元")

    if base_result_combined['年度个税'] < base_result_separate['年度个税']:
        print(f"   💡 建议: 并入综合所得方式更优，可节省个税 {base_result_separate['年度个税'] - base_result_combined['年度个税']:,.0f} 元")
    else:
        print(f"   💡 建议: 单独计税方式更优，可节省个税 {base_result_combined['年度个税'] - base_result_separate['年度个税']:,.0f} 元")


if __name__ == "__main__":
    main()