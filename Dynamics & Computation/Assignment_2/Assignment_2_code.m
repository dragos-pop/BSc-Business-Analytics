function [zero, approximates] = secant(func,x0,x1,tol,nmax)
% SECANT Find function zeros
%   ZERO=SECANT(FUN,X0,X1,tol,nmax) tries to find the zero ZERO of the
%   function of a real variable FUN by iteratively drawing a straight line 
%   through the previous two points on the graph and taking the zero of 
%   that line starting from the initial guesses X0 and X1
%
%   [ZERO, APPROXIMATES] = SECANT(FUN,...) returns the calculated ZERO and
%   a vector APPROIMATES of approximate values obtained in iterations
% 
%   tol = tolerance (accuracy), used to stop the program if the error 
%   (difference between X(k) and X(k-1) at the respective step is smaller than 
%   this (optional: if not entered by the user, it is assigned 0.0001
%   default value)
%
%   nmax = maximum number of iterations (optional: if not entered by the
%   user, it is assigned 1000 default value)
%
%
%   *The program does not allow the user to have nmax in input but no tol

% (2.) Converts nmax to optional (only works if user puts tol in input)
if ~exist('nmax')  % Checks if maximum number of iterations is not part of the input
    nmax = 1000; % Assigns default value 1000 in that case
end

% (3.) Converts tol to optional
if ~exist('tol')  % Checks if tolerance is not part of the input
    tol = 0.0001; % Assigns default value 0.0001 in that case
end

fk_1 = func(x0); % Evaluates the function at x0
fk = func(x1); % Evaluates the function at x1
approximates = x0; 
niter = 0;
diff = tol+1;

while  (abs(diff) >= tol & niter <= nmax) % Convergence condition: as long 
    % the difference between x1 and x0 (change in x) is not smaller than the given
    % tolerance and the current number of iterations is smaller than the
    % allowed limit, pursue with the next iteration
    niter = niter + 1; % iteration counter

    fk = func(x1); % Evaulates function af x1
    approximates = [approximates, x1]; % Stores the approximate values after each iteration
    diff = - fk * ((x1 - x0)/(fk - fk_1)); % change in x: second term of secant equation

    % Transforms the second point in the first point of the next iteration
    x0 = x1;
    fk_1 = fk;
 
    x1 = x1 + diff; % Secant equation
end

if niter > nmax
    fprintf(['secant stopped without converging to the desired tolerance',...
    ' because the maximum number of iterations was reached\n']);
end

zero = x1;

return
