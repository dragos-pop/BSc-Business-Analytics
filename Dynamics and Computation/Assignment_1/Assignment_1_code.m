function f = logistic(lambdaMin, lambdaMax, N)
% f = logistic(lambdaMin, lambdaMax, N)
%
% This function computes the logistic map (xn+1 = λxn(1 − xn))for a
% sequence of N values between lambdaMin and lambdaMax and plots the result
% in a picture with lambda values on the horizontal axis and xn on the 
% vertical one. 
%
% lambdaMin = the lowerbound of the interval, should be larger or equal to 
% 0 and smaller or equal to lambdaMax
%
% lambdaMax = the upperbound of the interval, should be larger or equal to
% lambdaMin and smaller or equal to 4
% 
% If the input does not respect the previous mentioned details, the program
% is not able to perform and outputs a warning message
%
% N = the number of of lambda values in the interval [lambdaMin, lambdaMax]
% and it is optional (i.e. the function works even if the input is only
% lambdaMin and lambdaMax). In case N is not specified by the user in the
% input, it takes a default value of 1000


    % (5.)Converts N to optional 
    if ~exist('N')  % Checks if N is not part of the input
        N = 1000; % Assigns value 1000 if it does not
    end
    
    %  (3.)Checks the input condition 0 ≤ λmin ≤ λmax ≤ 4 
    if (lambdaMin >=0) && (lambdaMin <= lambdaMax) && (lambdaMax <= 4)
        
        lambda = lambdaMin;
        
        % If lambdaMin equals lambdaMax, then there is a single lambda
        % value for which the logistic map is perfored and the variables
        % are assigned accordingly: x a vector with one dimension, step any
        % value larger than 0 (1 in this case, so that the current 
        % implementation of while-loop does not run forever) and 
        % lambdaValues equal to lambdaMin (or lambdaMax)
        if (lambdaMin == lambdaMax) 
            x = zeros(601, 1);
            step = 1;
            lambdaValues = lambdaMin;
        else
            % otherwise x initialised as a matrix with N+2 columns (such
            % that includes value for the boundaries lambdaMin and
            % lambdaMax, step the distance between any two adjacent lambdas
            % and lambdaValues ranging from lambdaMin to lambdaMax with a
            % distance on step in between values
            x = zeros(601, N+2);
            step = (lambdaMax - lambdaMin)/(N + 1); 
            lambdaValues = (lambdaMin:step:lambdaMax);  
        end
        
        x(1,:) = 0.2; %x0 actually is initialised
        % (1.) As one can see from the function(xn+1 = λxn(1 − xn)), when
        % x0 is 0 or 1 it yields a steady state of 0. Also, it was noticed
        % that x0 can be restricted to [0,0.5], due to xn(1-xn), because
        % the result is the same for x0=0.2 as it is for x0=0.8 for
        % instance. Hence, multiple tries for x0 belonging to (0,0.5) were
        % performed, nevertheless all led to the same figure. In
        % conclusion, the value of x0 is not relevant to the final picture
        % as long as it belongs to (0, 1).
        
        j = 1;
        % Iterates over all lambda values in the sequence
        while (lambda <= lambdaMax) 
            % For every lambda, an orbit of size 600 is computed (according
            % to the theory of Clapter 10.2 ("allows the system to settle
            % down to its eventual behavior")) by using the result from the
            % previous iteration
            for i = 1:600 
                x(i+1,j) = lambda * x(i, j) * (1 - x(i, j));  
            end
            lambda = lambda + step;
            j = j + 1;
        end

        xn = x(301:601,:); % (A. 2) Only the last 300 values (i.e. n = 
        % {301, 302, ..., 600} are used in the picture to allow the system
        % to settle down
        
        % (4) Produces a plot with values of lambda on the horizontal
        % axis and xn values on the vertical one
        plot(lambdaValues, xn,".", "MarkerEdgeColor", "b"); 
        title('Orbit diagram')
        xlabel('λ')
        ylabel('X')
       
% 
    else %(3.)if the input condition (0 ≤ λmin ≤ λmax ≤ 4) is not satisfied
        % the function cannot be performed and informs the user about the
        % mistake
        disp('The function could not be performed because the input condition "0 ≤ λmin ≤ λmax ≤ 4" is not satisfied')
    end
    