%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Annabel Wing-Yan Fan for APS, 2024
% Version 1.2
% Last Updated: 11/4/2024
% Daniel Gurman: Added ability to produce rectangular backgrounds 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

stimuli_path = "C:\Users\danielgurman\OneDrive - Meta\Documents\GitHub\margaret-river\Time To Fuse\assets\Backgrounds\Noise\lab\";

nImages = 1;

width = 3840;
height = 2160;
figure

for i = 1:nImages
    % create 2D white noise from a normal distribution
    noise = randn([height,width]);
   
    % transform into frequency domain 
    noise = fftshift(fft2(noise));



    % create filter
    a = 1; % Parameter 3. 1/fᵅ exponent
    % d = ((1:imgSize)-(imgSize/2)-1).^2;
    % dd = sqrt(d(:) + d(:)');
    d_x = ((1:width)-(width/2)-1).^2;
    d_y = ((1:height)-(height/2)-1).^2;
    dd = sqrt(d_y(:) + d_x(:)');
    filt = dd .^ -a; % frequency filter
    filt(isinf(filt))=1; % replace +/-inf at DC or zero-frequency component

    % take 1/f
    noise = noise.*filt;
    % transform back into spatial domain
    noise = ifft2(ifftshift(noise));
    %imshow(noise, []);

    % scale noise bScaled = rescale(b,-1,1); %?

    image = rescale(noise, 0, 1);

    % save noise
    % imwrite(image, fullfile(stimuli_path, sprintf('pinknoise_%d.png', i)), 'png');
    imagesc(image)
    colormap gray
end




