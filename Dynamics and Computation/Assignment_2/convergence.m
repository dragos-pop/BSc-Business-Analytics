function f = convergence(func,x0,x1,tol,nmax)
% CONVERGENCE Plots the order of convergence (4.)
%   The function starts by computing using the secant method of FUN with 
%   initial guesses X0 and X1 to get the zero and the vector of approximate 
%   values at each iteration. Then, for every iteration, it calculates and 
%   stores p as expressed in the formula from the Course Notes. Finally, it 
%   plots these values.
% 
%   tol = tolerance (accuracy), used to stop the program if the error 
%   (difference between X(k) and X(k-1) at the respective step is smaller than 
%   this (optional: if not entered by the user, it is assigned 0.0001
%   default value)
% 
%   nmax = maximum number of iterations (optional: if not entered by the
%   user, it is assigned 1000 default value)
% 
%   *The program does not allow the user to have nmax in input but no tol
%   *The program only works if Assignment_2_Pop with the same input works

[zero, approximates] = Assignment_2_Pop(func,x0,x1,tol,nmax)
c = size(approximates)
p = 0;
for i = 2:(c(2)-1)
    p = [p,real(log((approximates(i+1)-zero)/(approximates(i)-zero))/log((approximates(i)-zero)/(approximates(i-1)-zero)))];
end

plot(p)
title('Order of convergence')
xlabel('Iteration')
ylabel('P')