module combinational_logic_with_loop (
    input wire [7:0] A,              // 输入信号 A (8位)
    input wire [7:0] B,              // 输入信号 B (8位)
    input wire [2:0] loop_count,     // 循环次数控制信号 (0到7)
    output reg [7:0] result,         // 输出结果
    output reg overflow_flag         // 溢出标志
);

    // 内部信号声明
    reg [7:0] temp_result;           // 临时存储中间结果
    integer i;                       // 循环计数器

    // 组合逻辑块
    always @(*) begin
        temp_result = A;             // 初始化临时结果为 A
        overflow_flag = 1'b0;        // 初始化溢出标志为 0

        // 使用 for 循环实现累加操作
        for (i = 0; i < loop_count; i = i + 1) begin
            if (temp_result + B > 8'hFF) begin
                overflow_flag = 1'b1; // 检测溢出
            end else begin
                temp_result = temp_result + B; // 累加 B
            end
        end

        // 将最终结果赋值给输出
        result = temp_result;
    end

endmodule