`define macro1 8'hFF
module test (
    input wire [7:0] a,b,
    output wire [7:0] y1,y2
);

    assign y1 = a + b; 
    assign y2 = (a - b) ^ a;
endmodule